package com.nr.test.servlet;

public class SleepFourthSecServlet extends MetricServlet {

    @Override
    protected long doWork() throws Exception {
        return sleep();
    }

    private long sleep() throws Exception {
        Thread.sleep(250);
        return 1;
    }

    @Override
    protected void initializeData() {
        // do nothing here
    }

}