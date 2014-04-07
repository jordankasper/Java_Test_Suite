package com.nr.test.servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class RumServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    public static final String TEST_HEADER = "TEST_HEADER";
    public static final String TEST_HEADER_VALUE = "TEST_HEADER CONTENT";

    int responseSize;

    @Override
    public void init(ServletConfig config) throws ServletException {
        super.init(config);
    }

    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        String sleep_milliseconds = req.getParameter("sleep_milliseconds");
        if (sleep_milliseconds != null) {
            try {
                Thread.sleep(Integer.parseInt(sleep_milliseconds));
            } catch (java.lang.InterruptedException e) {
            }
        }

        String status_code = req.getParameter("status_code");
        if (status_code != null) {
            resp.setStatus(Integer.parseInt(status_code));
        }

        String responseSizeParam = req.getParameter("response_size");
        if (responseSizeParam != null) {
            responseSize = Math.max(0, Integer.valueOf(responseSizeParam));
        }

        resp.addHeader(TEST_HEADER, TEST_HEADER_VALUE);

        writeResponse(resp);
    }

    protected List<String> getResponses() {
        List<String> responses = new ArrayList<String>();
        responses.add("<html>");
        responses.add("<head>");
        responses.add("<title>rum servlet</title>");
        responses.add(com.newrelic.api.agent.NewRelic.getBrowserTimingHeader());
        // responses.add("<%= com.newrelic.api.agent.NewRelic.getBrowserTimingHeader() %>");
        responses.add("<style type=\"text/css\">");
        responses.add("h1{text-align:center; background:#dddddd;color:#000000}");
        responses.add("body{font-family:sans-serif, arial; font-weight:normal}");
        responses.add("</style>");
        responses.add("</head>");
        responses.add(getResponseBody());
        // responses.add("<%= com.newrelic.api.agent.NewRelic.getBrowserTimingFooter() %>");
        responses.add(com.newrelic.api.agent.NewRelic.getBrowserTimingFooter());
        responses.add("</body></html>");
        return responses;
    }

    private String getResponseBody() {
        String beginBody = "<body>";
        StringBuilder sb = new StringBuilder();
        sb.append(beginBody);
        for (int i = 0; i < responseSize; i++) {
            sb.append(0);
        }
        return sb.toString();
    }

    protected void writeResponse(HttpServletResponse resp) throws IOException {
        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();
        List<String> responses = getResponses();
        for (String response : responses) {
            out.println(response);
        }
        out.close();
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        processRequest(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        processRequest(req, resp);
    }

    @Override
    public String getServletInfo() {
        return "rum servlet";
    }
}
