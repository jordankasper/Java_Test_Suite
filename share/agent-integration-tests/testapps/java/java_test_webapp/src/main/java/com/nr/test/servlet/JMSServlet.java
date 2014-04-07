/**
 * 
 */
package com.nr.test.servlet;

import java.io.IOException;
import java.lang.reflect.Method;
import java.util.Date;
import java.util.Random;

import javax.jms.Connection;
import javax.jms.ConnectionFactory;
import javax.jms.DeliveryMode;
import javax.jms.Destination;
import javax.jms.Message;
import javax.jms.MessageConsumer;
import javax.jms.MessageListener;
import javax.jms.MessageProducer;
import javax.jms.Session;
import javax.jms.TextMessage;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.apache.activemq.broker.BrokerService;
import org.hornetq.api.core.TransportConfiguration;
import org.hornetq.api.jms.HornetQJMSClient;
import org.hornetq.api.jms.JMSFactoryType;
import org.hornetq.core.remoting.impl.netty.NettyConnectorFactory;
import org.hornetq.jms.client.HornetQConnectionFactory;

/**
 * @author ddelany
 */
public class JMSServlet extends TestServlet {

    /** Warning shaddup */
    private static final long serialVersionUID = 814991478284103355L;

    // Query string parameters

    private static final String QS_PROVIDER = "provider";
    private static final String PROVIDER_APACHE = "activemq";
    private static final String PROVIDER_HORNET = "hornetq";
    private static final String DEFAULT_PROVIDER = PROVIDER_APACHE;

    // Query string values

    private String qsProvider = null;

    // This value is hardwired in the conf file for Hornet because Hornet cannot
    // create queues dynamically. If changed in either place must manually change the other.
    private static final String QUEUE_NAME = "AitTestQueue";

    private static final String getParamWithDefault(HttpServletRequest req, String paramName, String paramDefault) {
        String result = req.getParameter(paramName);
        if (result == null || result.length() == 0) {
            result = paramDefault;
        }
        return result;
    }

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        qsProvider = getParamWithDefault(req, QS_PROVIDER, DEFAULT_PROVIDER);

        Server server = null;
        Client client = null;

        try {
            server = new Server(qsProvider);
            server.start(QUEUE_NAME);

            client = new Client(qsProvider);
            client.sendSingle(QUEUE_NAME);

            pr("back from sendSingle()");

        } finally {
            try {
                if (server != null) {
                    server.shutdown();
                }
            } catch (Exception e) {
                System.err.println("JMSServlet: server shutdown:");
                e.printStackTrace(System.err);
            }
            try {
                if (client != null) {
                    client.shutdown();
                }
            } catch (Exception e) {
                System.err.println("JMSServlet: client shutdown:");
                e.printStackTrace(System.err);
            }
        }

        super.processRequest(req, resp);
        return;
    }

    @Override
    public String getServletInfo() {
        return "JMS servlet";
    }

    // Example from http://activemq.apache.org/how-should-i-implement-request-response-with-jms.html

    private static void pr(String msg) {
        System.err.println(new Date().toString() + ": JMSServlet: " + msg);
        System.err.flush();
    }

    // Solve the "annoying close()" problem once and for all.
    private static final void close(Object obj) {
        pr("closing " + obj + "...");
        if (obj != null) {
            try {
                Method m = obj.getClass().getMethod("close", new Class<?>[0]);
                m.invoke(obj, new Object[0]);
                pr("no exception thrown during the close.");
            } catch (Throwable th) {
                pr("while closing " + obj + ": " + th + " - ignored.");
            }
        }
    }

    private static class Server implements MessageListener {
        private static final int ACK_MODE = Session.AUTO_ACKNOWLEDGE;
        private static final String MESSAGE_BROKER_URL = "tcp://localhost:61616";
        private static final boolean TRANSACTED = false;

        private static BrokerService broker;

        private ConnectionFactory connectionFactory;
        private Connection connection;
        private Session session;
        private MessageProducer replyProducer;

        /**
         * Create a Server using one of the supported providers
         * 
         * @param qsProvider the provider
         * @throws IllegalArgumentException - unrecognized provider
         */
        public Server(String qsProvider) {
            if (qsProvider.equals(PROVIDER_APACHE)) {
                setupApacheMQ();
            } else if (qsProvider.equals(PROVIDER_HORNET)) {
                setupHornetQ();
            } else {
                throw new IllegalArgumentException("JMSServlet: unsupported queue provider type: " + qsProvider);
            }
            pr("initialized Server JMS.");
        }

        // ApacheMQ-specific setup
        private void setupApacheMQ() {
            try {
                // This message broker is embedded
                if (broker != null) {
                    broker = new BrokerService();
                    broker.setPersistent(false);
                    broker.setUseJmx(false);
                    broker.addConnector(MESSAGE_BROKER_URL);
                    broker.start();
                }
                connectionFactory = new ActiveMQConnectionFactory(MESSAGE_BROKER_URL);
            } catch (Exception e) {
                pr("Server():");
                e.printStackTrace(System.err);
            }
        }

        // HornetQ-specific setup
        private void setupHornetQ() {
            TransportConfiguration transportConfiguration = new TransportConfiguration(
                    NettyConnectorFactory.class.getName());
            HornetQConnectionFactory hqcf = HornetQJMSClient.createConnectionFactoryWithoutHA(JMSFactoryType.CF,
                    transportConfiguration);
            hqcf.setUseGlobalPools(false);
            if (hqcf instanceof ConnectionFactory) {
                connectionFactory = (ConnectionFactory) hqcf;
            } else {
                pr("Server(): setupHornetQ(): not a connection factory: " + hqcf);
            }
        }

        // This method is not provider-specific. It's from setupMessageQueueConsumer() in the example code.
        public void start(String queueName) {
            try {
                connection = connectionFactory.createConnection();
                connection.start();
                this.session = connection.createSession(TRANSACTED, ACK_MODE);
                // On ActiveMQ this creates the queue dynamically. On HornetQ,
                // it just opens the queue created in the conf file.
                Destination adminQueue = this.session.createQueue(queueName);

                // Setup a message producer to respond to messages from clients, we will get the destination
                // to send to from the JMSReplyTo header field from a Message
                this.replyProducer = this.session.createProducer(null);
                this.replyProducer.setDeliveryMode(DeliveryMode.NON_PERSISTENT);

                // Set up a consumer to consume messages off of the admin queue
                MessageConsumer consumer = this.session.createConsumer(adminQueue);
                consumer.setMessageListener(this);
            } catch (Exception e) {
                pr("Server start():");
                e.printStackTrace(System.err);
            }
        }

        // This method is not provider-specific
        @Override
        public void onMessage(Message message) {
            try {
                // This is a hack. With HornetQ, this transaction completes so fast that the Agent typically
                // doesn't send it to the Collector. So we have to slow it down.
                Thread.sleep(50);

                TextMessage response = this.session.createTextMessage();
                if (message instanceof TextMessage) {
                    TextMessage txtMsg = (TextMessage) message;
                    String messageText = txtMsg.getText();
                    pr("Server: received from client: \"" + messageText + "\"");
                    response.setText("JMSServlet: request was successfully processed.");
                }

                // Set the correlation ID from the received message to be the correlation id of the response message
                // this lets the client identify which message this is a response to if it has more than
                // one outstanding message to the server
                response.setJMSCorrelationID(message.getJMSCorrelationID());

                // Send the response to the Destination specified by the JMSReplyTo field of the received message,
                // this is presumably a temporary queue created by the client
                this.replyProducer.send(message.getJMSReplyTo(), response);
            } catch (Exception e) {
                pr("Server: onMessage():");
                e.printStackTrace(System.err);
            }
        }

        public void shutdown() throws Exception {
            close(session);
            close(connection);
            close(connectionFactory);
        }
    }

    private static class Client implements MessageListener {
        private static final String MESSAGE_BROKER_URL = "tcp://localhost:61616";
        private static final int ACK_MODE = Session.AUTO_ACKNOWLEDGE;
        private static final boolean TRANSACTED = false;

        private Session session;
        private Connection connection;
        private ConnectionFactory connectionFactory;
        private MessageProducer producer;

        public Client(String qsProvider) {
            if (qsProvider.equals(PROVIDER_APACHE)) {
                setupApacheMQ();
            } else if (qsProvider.equals(PROVIDER_HORNET)) {
                setupHornetQ();
            } else {
                throw new IllegalArgumentException("JMSServlet: unsupported queue provider type: " + qsProvider);
            }
            pr("initialized Client JMS.");
        }

        // ApacheMQ-specific setup
        private void setupApacheMQ() {
            try {
                connectionFactory = new ActiveMQConnectionFactory(MESSAGE_BROKER_URL);
            } catch (Exception e) {
                pr("Client():");
                e.printStackTrace(System.err);
            }
        }

        // HornetQ-specific setup
        private void setupHornetQ() {
            TransportConfiguration transportConfiguration = new TransportConfiguration(
                    NettyConnectorFactory.class.getName());
            HornetQConnectionFactory hqcf = HornetQJMSClient.createConnectionFactoryWithoutHA(JMSFactoryType.CF,
                    transportConfiguration);
            hqcf.setUseGlobalPools(false);
            if (hqcf instanceof ConnectionFactory) {
                connectionFactory = (ConnectionFactory) hqcf;
            } else {
                pr("Server(): setupHornetQ(): not a connection factory: " + hqcf);
            }
        }

        public void sendSingle(String queueName) {
            try {
                connection = connectionFactory.createConnection();
                connection.start();
                session = connection.createSession(TRANSACTED, ACK_MODE);
                Destination adminQueue = session.createQueue(queueName);

                // Setup a message producer to send message to the queue the server is consuming from
                this.producer = session.createProducer(adminQueue);
                this.producer.setDeliveryMode(DeliveryMode.NON_PERSISTENT);

                // Create a temporary queue that this client will listen for responses on then create a consumer
                // that consumes message from this temporary queue...for a real application a client should reuse
                // the same temp queue for each message to the server...one temp queue per client
                Destination tempDest = session.createTemporaryQueue();
                MessageConsumer responseConsumer = session.createConsumer(tempDest);

                // This class will handle the messages to the temp queue as well
                // We now use synchronous receive here
                // responseConsumer.setMessageListener(this);

                // Now create the actual message you want to send
                TextMessage txtMessage = session.createTextMessage();
                txtMessage.setText("JMSServlet: this client request was generated " + new Date());

                // Put some parameters on the message in order to test our ability to capture them.
                // The test must enable this capability in the Agent config in order to test it.
                txtMessage.setBooleanProperty("BooleanTrue", true);
                txtMessage.setByteProperty("Byte42", (byte) 42);
                txtMessage.setDoubleProperty("Double42dot42", 42.42);
                txtMessage.setFloatProperty("Float42dot4", 42.4F);
                txtMessage.setIntProperty("Int43", 43);
                txtMessage.setStringProperty("StringHello", "Hello");
                txtMessage.setStringProperty("IgnoredShouldNotAppearInTestResult",
                        "AN ERROR HAS OCCURRED IF THIS APPEARS IN THE TEST RESULT");

                // Set the reply to field to the temp queue you created above, this is the queue the server
                // will respond to
                txtMessage.setJMSReplyTo(tempDest);

                // Set a correlation ID so when you get a response you know which sent message the response is for
                // If there is never more than one outstanding message to the server then the
                // same correlation ID can be used for all the messages...if there is more than one outstanding
                // message to the server you would presumably want to associate the correlation ID with this
                // message somehow...a Map works good
                String correlationId = this.createRandomString();
                txtMessage.setJMSCorrelationID(correlationId);
                pr("client sending...");
                this.producer.send(txtMessage);
                pr("client sent 1 message, receiving...");
                Message m = responseConsumer.receive();
                processMessage(m);
            } catch (Exception e) {
                pr("Client():");
                e.printStackTrace(System.err);
            }
        }

        public void shutdown() throws Exception {
            close(session);
            close(connection);
            close(connectionFactory);
        }

        private String createRandomString() {
            Random random = new Random(System.currentTimeMillis());
            long randomLong = random.nextLong();
            return Long.toHexString(randomLong);
        }

        /**
         * The Client implementation doesn't use this onMessage(), preferring instead a synchronous receive();
         */
        @Override
        public void onMessage(Message message) {
            processMessage(message);
        }

        private void processMessage(Message message) {
            String messageText = null;
            try {
                if (message instanceof TextMessage) {
                    TextMessage textMessage = (TextMessage) message;
                    messageText = textMessage.getText();
                    pr("client: received from Server: \"" + messageText + "\"");
                }
            } catch (Exception e) {
                pr("Client: onMessage():");
                e.printStackTrace(System.err);
            }
        }
    }
}