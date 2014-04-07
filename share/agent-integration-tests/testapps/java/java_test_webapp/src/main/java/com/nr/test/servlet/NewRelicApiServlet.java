package com.nr.test.servlet;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.util.Date;
import com.newrelic.api.agent.NewRelic;

public class NewRelicApiServlet extends TestServlet {

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
            } else if (api.equals("addCustomParameter")) {
                NewRelic.addCustomParameter(api_args[0], api_args[1]);
            }
        }

        super.processRequest(req, resp);
    }

    public String getServletInfo() {
        return "New Relic API test servlet";
    }
}
