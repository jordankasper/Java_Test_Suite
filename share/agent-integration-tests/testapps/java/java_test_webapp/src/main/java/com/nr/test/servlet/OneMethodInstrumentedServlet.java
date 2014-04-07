package com.nr.test.servlet;

public class OneMethodInstrumentedServlet extends MetricServlet {

    @Override
    protected long doWork() {
        return sumTimeDigits();
    }

    private long sumTimeDigits() {
        long value = 0;
        long time = System.nanoTime();
        char[] daTime = String.valueOf(time).toCharArray();
        for (char current : daTime) {
            value += Integer.parseInt(String.valueOf(current));
        }
        return value;
    }

    @Override
    protected void initializeData() {

    }

}