package com.nr.test.servlet;

import java.util.Random;

public class OneThreadServlet extends MetricServlet {

    private static final int RAND_ARRAY_SIZE = 100;
    private static final int MOD_VALUE = 100;
    private static final Random RAND_GENERATOR = new Random();

    @Override
    protected void initializeData() {
        // do nothing here
    }

    @Override
    protected long doWork() throws Exception {
        return startThread();
    }

    public long startThread() throws Exception {
        Worker wk = new Worker();
        wk.start();
        try {
            wk.join();
        } catch (Exception e) {
            // do nothing in here
        }
        int totalOutput = wk.getOutput();
        if (totalOutput <= 0) {
            throw new Exception("The total output is not correct " + totalOutput);
        }
        return totalOutput;
    }

    private class Worker extends Thread {

        private int output = 0;

        Worker() {
            super();
        }

        @Override
        public void run() {
            int[] randoms = new int[RAND_ARRAY_SIZE];
            // create the random numbers
            for (int i = 0; i < randoms.length; i++) {
                randoms[i] = RAND_GENERATOR.nextInt(Integer.MAX_VALUE);
            }

            // mod and then add them
            for (int i = 0; i < randoms.length; i++) {
                output += randoms[i] % MOD_VALUE;
            }

        }

        public int getOutput() {
            return output;
        }
    }

}