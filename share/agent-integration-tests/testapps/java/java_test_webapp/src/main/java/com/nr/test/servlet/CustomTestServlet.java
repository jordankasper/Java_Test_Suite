package com.nr.test.servlet;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.util.Date;

public class CustomTestServlet extends TestServlet {


    @Override
    protected void processRequest(HttpServletRequest req,
            HttpServletResponse resp) throws ServletException, IOException {

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
        
        customTestMethod(req);
        customOtherTestMethod(req);

        writeResponse(resp);
    }
    
    /** 
     *  This is the method that we will look for in the custom metrics
     *  test.
     */
    private void customTestMethod(HttpServletRequest req) {
        String sleep_milliseconds = req.getParameter("sleep_milliseconds");
        if (sleep_milliseconds != null) {
            try {
                Thread.sleep(Integer.parseInt(sleep_milliseconds));
            } catch (java.lang.InterruptedException e) {
            }
        } else {
            try {
                Thread.sleep(100);
            } catch (java.lang.InterruptedException e) {
            }
        }
    }
    
    /** 
     *  This is the method that we will look for in the custom metrics
     *  test.
     */
    private void customOtherTestMethod(HttpServletRequest req) {
        String sleep_milliseconds = req.getParameter("sleep_milliseconds");
        if (sleep_milliseconds != null) {
            try {
                Thread.sleep(Integer.parseInt(sleep_milliseconds));
            } catch (java.lang.InterruptedException e) {
            }
        } else {
            try {
                Thread.sleep(100);
            } catch (java.lang.InterruptedException e) {
            }
        }
    }

}
