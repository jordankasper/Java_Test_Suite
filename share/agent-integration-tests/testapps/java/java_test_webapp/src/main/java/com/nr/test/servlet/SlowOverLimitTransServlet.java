package com.nr.test.servlet;

import com.newrelic.api.agent.Trace;
import java.io.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class SlowOverLimitTransServlet extends TestServlet {

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        run();

        String status_code = req.getParameter("status_code");
        if (status_code != null) {
            resp.setStatus(Integer.parseInt(status_code));
        }

        writeResponse(resp);
    }

    public String getServletInfo() {
        return "test servlet for transaction trace stack traces";
    }

    @Trace()
    public void run() {
        childInitiator();
    }

    @Trace
    private void childInitiator() {
        childone();
        childtwo();
        childthree();
        childfour();
        childfive();
        childsix();
        childseven();
    }

    @Trace
    private void childone() {
        sleepTime(1500);
    }

    @Trace
    private void childtwo() {
        sleepTime(1500);
    }

    @Trace
    private void childthree() {
        sleepTime(1500);
    }

    @Trace
    private void childfour() {
        sleepTime(1500);
    }

    @Trace
    private void childfive() {
        sleepTime(1500);
    }

    @Trace
    private void childsix() {
        sleepTime(1500);
    }

    @Trace
    private void childseven() {
        sleepTime(1500);
    }

    private void sleepTime(long time) {
        try {
            Thread.sleep(time);
        } catch (java.lang.InterruptedException e) {
        }
    }

}