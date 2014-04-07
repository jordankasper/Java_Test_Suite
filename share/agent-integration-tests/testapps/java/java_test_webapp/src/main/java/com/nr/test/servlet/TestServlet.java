package com.nr.test.servlet;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.util.Date;

public class TestServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    public void init(ServletConfig config) throws ServletException {
        super.init(config);
    }

    public void destroy() { }

    protected void processRequest(HttpServletRequest req, HttpServletResponse resp)
		throws ServletException, IOException {

		String sleep_milliseconds = req.getParameter("sleep_milliseconds");
		if (sleep_milliseconds != null) {
			try {
				Thread.sleep(Integer.parseInt(sleep_milliseconds));
			} catch (java.lang.InterruptedException e) { }
		}

		String status_code = req.getParameter("status_code");
		if (status_code != null) {
			resp.setStatus(Integer.parseInt(status_code));
		}

		writeResponse(resp);
    }


	protected void writeResponse(HttpServletResponse resp) throws IOException {
        resp.setContentType("text/html;charset=UTF-8");
		PrintWriter out = resp.getWriter();
        out.println("<html>");
        out.println("<head>");
        out.println("<title>test servlet</title>");
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

    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
		throws ServletException, IOException {
        processRequest(req, resp);
    }

    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
		throws ServletException, IOException {
        processRequest(req, resp);
    }

    public String getServletInfo() {
        return "test servlet";
    }
}
