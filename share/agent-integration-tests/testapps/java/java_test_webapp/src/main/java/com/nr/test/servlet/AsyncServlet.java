package com.nr.test.servlet;

import java.io.IOException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import javax.servlet.AsyncContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.newrelic.api.agent.Trace;

/**
 * Servlet 3.0 async test servlet.
 */
@WebServlet(urlPatterns = "/AsyncServlet", asyncSupported = true)
public class AsyncServlet extends HttpServlet {

	private static final long serialVersionUID = 1L;
	private static final ScheduledExecutorService EXECUTOR = Executors.newSingleThreadScheduledExecutor();
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public AsyncServlet() {
        super();
    }

    @Override
    public void destroy() {
        EXECUTOR.shutdown();
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		final AsyncContext ac = request.startAsync();
        EXECUTOR.schedule(new Runnable() {
			@Trace(dispatcher=true)
			public void run() {
				ac.dispatch("/AsyncServlet2");
			}
		}, 1000L, TimeUnit.MILLISECONDS);
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
	}

}
