package com.nr.test.servlet;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class HttpUrlServlet extends TestServlet {

    private static final long serialVersionUID = 1L;

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        conductHttpRequest1();
        conductHttpRequest2();

        super.processRequest(req, resp);
    }

    private void conductHttpRequest1() {
        callHttpRequest("http", "news.yahoo.com", 80, "/world");
    }

    private void conductHttpRequest2() {
        callHttpRequest("http", "www.yahoo.com", 80, "/");
    }

    private void callHttpRequest(String schema, String host, int port, String path) {
        sun.net.www.protocol.http.HttpURLConnection connection = null;
        try {
            URL url = new URL(schema, host, port, path);
            connection = new sun.net.www.protocol.http.HttpURLConnection(url, null);
            connection.connect();
            InputStream is = connection.getInputStream();
            int length = is.available();
            if (length > 0) {
                byte[] data = new byte[length];
                is.read(data, 0, data.length);
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    @Override
    public String getServletInfo() {
        return "external call http url servlet";
    }
}