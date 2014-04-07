package com.nr.test.servlet;

import java.io.IOException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.eclipse.jetty.continuation.Continuation;
import org.eclipse.jetty.continuation.ContinuationSupport;

import com.newrelic.api.agent.Trace;

/**
 * Servlet implementation class JettyContinuations7Servlet
 */
public class Jetty7ContinuationsServlet extends HttpServlet {
       
	private static final long serialVersionUID = 1L;
	private static final ScheduledExecutorService EXECUTOR = Executors.newSingleThreadScheduledExecutor();
       
	private final Object lock = new Object();

    /**
     * @see HttpServlet#HttpServlet()
     */
    public Jetty7ContinuationsServlet() {
        super();
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        final String complete = request.getParameter("complete");
        String quotes = (String) request.getAttribute("quotes");
		if (quotes == null) {
	 		final Continuation continuation = ContinuationSupport.getContinuation(request);
	  		continuation.setTimeout(0L);
			continuation.suspend();
			EXECUTOR.schedule(new Runnable() {
				@Trace(dispatcher=true)
				public void run() {
					synchronized (lock) {
					    if (complete == null) {
	                        continuation.setAttribute("quotes", "async results");
	                        continuation.resume();
					    } else {
					        try {
					            continuation.getServletResponse().getWriter().println("async results");
					            continuation.complete();
					        } catch (IOException e) {
					            //ignore
					        }
					    }
					}
				}
			}, 1000L, TimeUnit.MILLISECONDS);
		} else {
        	response.getWriter().println(quotes);
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
	}

}
