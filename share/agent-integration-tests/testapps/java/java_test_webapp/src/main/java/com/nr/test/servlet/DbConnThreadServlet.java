package com.nr.test.servlet;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * This servlet is designed to test the case where the connection is created in a separate thread as the main execution
 * thread.
 */
public class DbConnThreadServlet extends TestServlet {

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        String sql = req.getParameter("sql");
        if (sql == null) {
            sql = "select test_column from test_table";
        }
        String engine = req.getParameter("engine");

        System.out.println("Process Request: " + engine + ": " + sql);

        ExecutorService executor = Executors.newFixedThreadPool(1);
        CreateStatementThread worker = new CreateStatementThread(engine);

        try {
            Future<Connection> output = executor.submit(worker);
            // since we really are just waiting for the thread to complete - we can block
            runQuery(output.get(), sql);
        } catch (Exception e) {
            e.printStackTrace(System.out);
            throw new RuntimeException(e);
        } finally {
            worker.closeConnection();
            executor.shutdown();
        }

        super.processRequest(req, resp);
    }

    private void runQuery(Connection conn, String sql) throws SQLException {
        System.out.println("Running the query");
        PreparedStatement cs = conn.prepareStatement(sql);
        ResultSet rs = cs.executeQuery();
        ResultSetMetaData rmd = rs.getMetaData();

        int num_cols = rmd.getColumnCount();
        while (rs.next()) {
            for (int i = 1; i < num_cols; ++i) {
                rmd.getColumnName(i);
                rs.getString(i);
            }
            rmd.getColumnName(num_cols);
            rs.getString(num_cols);
        }
    }

    @Override
    public String getServletInfo() {
        return "DB Thread servlet";
    }

    public class CreateStatementThread implements Callable<Connection> {

        private final String engine;
        private Connection conn = null;

        public CreateStatementThread(String pEngine) {
            engine = pEngine;
        }

        @Override
        public Connection call() throws Exception {
            System.out.println("Creating the PreparedStatement");
            conn = createConnection(engine);
            return conn;
        }

        public void closeConnection() {
            if (conn != null) {
                try {
                    conn.close();
                } catch (SQLException e) {
                    // ignore
                }
            }
        }

        private Connection createConnection(String engine) throws Exception {
            if ("oracle".equals(engine)) {
                System.out.println("testing in Oracle");
                Class.forName("oracle.jdbc.driver.OracleDriver").newInstance();
                return DriverManager.getConnection("jdbc:oracle:thin:@172.16.1.87:1521:orcl", "system", "oracle");
            } else if ("postgres".equals(engine)) {
                System.out.println("testing in Postgres");
                Class.forName("org.postgresql.Driver").newInstance();
                return DriverManager.getConnection("jdbc:postgresql://172.16.2.236:5432/agent_test_pdql?user=agent_test&password=@gent!!!p");
            } else { // fall back to mysql
                System.out.println("testing in MySQL");

                Class.forName("com.mysql.jdbc.Driver").newInstance();
                return DriverManager.getConnection("jdbc:mysql://172.16.2.236/agent_test?user=agent_test&password=@g3nt!!!");
            }
        }
    }

}
