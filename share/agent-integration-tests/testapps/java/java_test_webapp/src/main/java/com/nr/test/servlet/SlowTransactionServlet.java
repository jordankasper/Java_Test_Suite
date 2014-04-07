package com.nr.test.servlet;

import com.newrelic.api.agent.Trace;
import java.io.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class SlowTransactionServlet extends TestServlet {

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        firstMethod();

        String status_code = req.getParameter("status_code");
        if (status_code != null) {
            resp.setStatus(Integer.parseInt(status_code));
        }

        writeResponse(resp);
    }

    @Trace
    private void firstMethod() {
        secondMethod();
    }

    @Trace
    private void secondMethod() {
        thirdMethod();
    }

    @Trace
    private void thirdMethod() {
        slowMethodOneA();
        slowMethodTwo();
    }

    @Trace
    private void slowMethodOneA() {
        sleep(1000);

        slowMethodOneB();
    }

    /** This node should have a stack trace. **/
    @Trace
    private void slowMethodOneB() {
        sleep(2000);
    }

    /** This node should have a stack trace. */
    @Trace
    private void slowMethodTwo() {
        sleep(3000);
    }

    private void sleep(long time) {
        try {
            Thread.sleep(time);
        } catch (java.lang.InterruptedException e) {
        }
    }

    public String getServletInfo() {
        return "test servlet for transaction trace stack traces";
    }
}