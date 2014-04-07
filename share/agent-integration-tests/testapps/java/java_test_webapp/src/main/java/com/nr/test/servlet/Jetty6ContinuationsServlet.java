package com.nr.test.servlet;

import java.io.IOException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.mortbay.util.ajax.Continuation;
import org.mortbay.util.ajax.ContinuationSupport;

import com.newrelic.api.agent.Trace;

/**
 * Servlet implementation class JettyContinuations6Servlet
 */
public class Jetty6ContinuationsServlet extends HttpServlet {
       
	private static final long serialVersionUID = 1L;
	private static final ScheduledExecutorService EXECUTOR = Executors.newSingleThreadScheduledExecutor();
       
	private final Object lock = new Object();

    /**
     * @see HttpServlet#HttpServlet()
     */
    public Jetty6ContinuationsServlet() {
        super();
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    	synchronized (lock) {
	    	final Continuation continuation = ContinuationSupport.getContinuation(request, lock);
	    	if (continuation.isNew()) {
        		EXECUTOR.schedule(new Runnable() {
					@Trace(dispatcher=true)
					public void run() {
						synchronized (lock) {
							continuation.setObject("async results");
							continuation.resume();
						}
					}
				}, 1000L, TimeUnit.MILLISECONDS);
	    		//this throws an org.mortbay.jetty.RetryRequest
	    		continuation.suspend(0L);
	    	} else {
	 	    	String result = (String) continuation.getObject();
	    		response.getWriter().println(result);
	    	}
    	}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
	}

}
