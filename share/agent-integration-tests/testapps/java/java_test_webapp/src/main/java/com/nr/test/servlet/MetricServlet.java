package com.nr.test.servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Date;
import java.util.concurrent.TimeUnit;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public abstract class MetricServlet extends HttpServlet {

    private static final double TO_MS_CONV = 1000000.0;
    private static final String ITERATION_COUNT_PARAM = "iteration_count";
    private static final String REPEAT_COUNT_PARAM = "repeat_count";
    private static final int DEFAULT_ITERATION_COUNT = 1000;
    private static final int DEFAULT_REPEAT_COUNT = 1;
    private static final int DEFAULT_EXCEPTION_COUNT = 2;
    private static final String RESULT_TIME_NS_PARAM = "result_time_sec";
    private static final String RESULT_SUCCESS_PARAM = "was_success";
    private static final String RESULT_NUM_PARAM = "work_result";

    @Override
    public void init(ServletConfig config) throws ServletException {
        super.init(config);

        initializeData();
        // call do work once for warm up
        try {
            doWork();
        } catch (Exception e) {
            // ignore here
        }
    }

    @Override
    public void destroy() {
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
        return "metric servlet";
    }

    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        int iterationCount = getIterationCount(req);
        int repeatCount = getRepeatCount(req);

        runTestAndAddResults(resp, iterationCount, repeatCount);

        String status_code = req.getParameter("status_code");
        if (status_code != null) {
            resp.setStatus(Integer.parseInt(status_code));
        }

        writeResponse(resp);
    }

    private void runTestAndAddResults(HttpServletResponse resp, int iterationCount, int repeatCount) {

        // set initial variables
        OutputInformation info = new OutputInformation();
        int timerRuns = 0;
        int exceptions = 0;

        // run the timed tests
        while ((timerRuns < repeatCount) && (exceptions < DEFAULT_EXCEPTION_COUNT)) {
            try {
                runOneTimer(iterationCount, info);
                timerRuns++;
            } catch (Exception e) {
                exceptions++;
            }
        }

        // set the headers
        if (info.isValid() && (timerRuns == repeatCount)) {
            resp.addHeader(RESULT_NUM_PARAM, info.getOutput());
            resp.addHeader(RESULT_TIME_NS_PARAM, info.getDurationMS());
            resp.addHeader(RESULT_SUCCESS_PARAM, "True");
            resp.addHeader(ITERATION_COUNT_PARAM, String.valueOf(iterationCount));
            resp.addHeader(REPEAT_COUNT_PARAM, String.valueOf(repeatCount));
        } else {
            resp.addHeader(RESULT_SUCCESS_PARAM, "False: IsValid:" + info.isValid() + " TimerRuns: " + timerRuns);
            resp.addHeader(ITERATION_COUNT_PARAM, String.valueOf(iterationCount));
            resp.addHeader(REPEAT_COUNT_PARAM, String.valueOf(repeatCount));
        }

    }

    private void runOneTimer(int iterationCount, OutputInformation info) throws Exception {
        long output = 0;
        long beginning = System.nanoTime();

        for (int i = 0; i < iterationCount; i++) {
            output += doWork();
        }

        long end = System.nanoTime();
        long duration = end - beginning;
        info.addInfo(duration, output);
    }

    private int getIterationCount(HttpServletRequest req) {
        String iterationCountString = req.getHeader(ITERATION_COUNT_PARAM);
        if (iterationCountString == null) {
            return DEFAULT_ITERATION_COUNT;
        } else {
            try {
                return Integer.parseInt(iterationCountString);
            } catch (NumberFormatException e) {
                return DEFAULT_ITERATION_COUNT;
            }
        }
    }

    private int getRepeatCount(HttpServletRequest req) {
        String repeatCountString = req.getHeader(REPEAT_COUNT_PARAM);
        if (repeatCountString == null) {
            return DEFAULT_REPEAT_COUNT;
        } else {
            try {
                return Integer.parseInt(repeatCountString);
            } catch (NumberFormatException e) {
                return DEFAULT_REPEAT_COUNT;
            }
        }
    }

    protected abstract long doWork() throws Exception;

    protected abstract void initializeData();

    protected void writeResponse(HttpServletResponse resp) throws IOException {
        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();
        out.println("<html>");
        out.println("<head>");
        out.println("<title>metric servlet</title>");
        out.println("<style type=\"text/css\">");
        out.println("h1{text-align:center; background:#dddddd;color:#000000}");
        out.println("body{font-family:sans-serif, arial; font-weight:normal}");
        out.println("</style>");
        out.println("</head>");
        out.println("<body>");
        out.println("<h1>" + getServletInfo() + "</h1>");
        out.println("<br><br><hr>" + new Date().toString());
        out.println("</body>");
        out.println("</html>");
        out.close();
    }

    private class OutputInformation {
        private long duration = 0;
        private long output = 0;

        OutputInformation() {
            super();
        }

        boolean isValid() {
            // just make sure something has changed
            return (duration != 0) || (output != 0);
        }

        void addInfo(long pDuration, long pOutput) {
            if ((duration == 0) || (pDuration < duration)) {
                duration = pDuration;
                output = pOutput;
            }
        }

        String getDurationMS() {
            double durationSec = (double) duration / TO_MS_CONV;
            return Double.valueOf(durationSec).toString();
        }

        String getOutput() {
            return Long.valueOf(output).toString();
        }
    }

}