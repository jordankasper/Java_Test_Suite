package com.nr.test.servlet;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.util.Date;
import com.newrelic.api.agent.NewRelic;

public class WaitTimeServlet extends TestServlet {

    @Override
    public void init(ServletConfig config) throws ServletException {
        super.init(config);

        try {
            Thread.sleep(4000);
        } catch (InterruptedException e) {
            // do nothing
        }
    }

    protected void processRequest(HttpServletRequest req,
            HttpServletResponse resp) throws ServletException, IOException {

        String api = req.getParameter("api");
        String arg_str = req.getParameter("api_args");
        String[] api_args = (arg_str == null ? new String[] {} : arg_str
                .split(","));

        if (api != null) {
            if (api.equals("recordResponseTimeMetric")) {
                NewRelic.recordResponseTimeMetric(api_args[0],
                        Integer.parseInt(api_args[1]));
            } else if (api.equals("setTransactionName")) {
                NewRelic.setTransactionName(null, api_args[0]);
            } else if (api.equals("recordMetric")) {
                NewRelic.recordMetric(api_args[0],
                        Integer.parseInt(api_args[1]));
            }
        }

        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            // do nothing
        }

        writeResponse(resp);
    }

    public String getServletInfo() {
        return "New Relic API test servlet";
    }

}