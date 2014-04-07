package com.nr.test.servlet;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.Reader;
import java.io.StringWriter;
import java.io.Writer;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;

/**
 * A servlet that makes an external call and returns its output.
 * 
 */
public class ExternalCallServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final String APP_DATA_HEADER = "X-NewRelic-App-Data";

    String outputString = null;
    private String appDataHeader;
    private String testHeader;

    @Override
    public void init(ServletConfig config) throws ServletException {
        super.init(config);
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        processRequest(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        processRequest(req, resp);
    }

    private void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

        String sleep_milliseconds = req.getParameter("sleep_milliseconds");
        if (sleep_milliseconds != null) {
            try {
                Thread.sleep(Integer.parseInt(sleep_milliseconds));
            } catch (java.lang.InterruptedException e) {
            }
        }

        String url = req.getParameter("url");
        if (url == null) {
            return;
        }

        String responseSizeParam = req.getParameter("response_size");
        if (responseSizeParam != null) {
            int responseSize = Math.max(0, Integer.valueOf(responseSizeParam));
            StringBuilder sb = new StringBuilder(url);
            if (url.indexOf('?') == -1) {
                sb.append("?response_size=").append(String.valueOf(responseSize));
            } else {
                sb.append("&response_size=").append(String.valueOf(responseSize));
            }
            url = sb.toString();
        }

        String method = req.getParameter("method");
        if (method.equals("HttpClient_3")) {
            HttpClient_3(url);
        } else if (method.equals("HttpClient_4")) {
            HttpClient_4(url);
        } else if (method.equals("HttpURLConnection")) {
            HttpURLConnection(url);
        }

        if (appDataHeader != null) {
            resp.addHeader(APP_DATA_HEADER, appDataHeader);
        }

        if (testHeader != null) {
            resp.addHeader(TestServlet2.TEST_HEADER, testHeader);
        }

        if (outputString != null) {
            writeResponse(resp, outputString);
        }
    }

    private void HttpClient_3(String url) throws IOException {
        HttpClient httpClient = new HttpClient();
        HttpMethod method = new GetMethod(url);
        httpClient.executeMethod(method);
    }

    private void HttpClient_4(String url) throws IOException {
        org.apache.http.client.HttpClient httpClient = new DefaultHttpClient();
        HttpUriRequest httpget = new HttpGet(url);
        httpClient.execute(httpget);
    }

    private void HttpURLConnection(String urlString) throws IOException {
        HttpURLConnection urlc = null;
        try {
            URL url = new URL(urlString);
            urlc = (HttpURLConnection) url.openConnection();
            InputStream in = urlc.getInputStream();
            appDataHeader = urlc.getHeaderField(APP_DATA_HEADER);
            testHeader = urlc.getHeaderField(TestServlet2.TEST_HEADER);
            try {
                Writer writer = new StringWriter();
                Reader reader = new InputStreamReader(in);
                pipe(reader, writer);
                reader.close();
                outputString = writer.toString();
            } finally {
                if (in != null) {
                    in.close();
                }
            }
        } finally {
            if (urlc != null) {
                urlc.disconnect();
            }
        }
    }

    private void pipe(Reader reader, Writer writer) throws IOException {
        char buf[] = new char[1024];
        for (int read = 0; (read = reader.read(buf)) >= 0;) {
            writer.write(buf, 0, read);
        }
        writer.flush();
    }

    private void writeResponse(HttpServletResponse resp, String outputString) throws IOException {
        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();
        out.write(outputString);
        out.close();
        resp.setContentLength(outputString.length());
    }

}
