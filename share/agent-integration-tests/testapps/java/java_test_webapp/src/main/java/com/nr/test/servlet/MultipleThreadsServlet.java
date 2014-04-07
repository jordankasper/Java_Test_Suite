package com.nr.test.servlet;


public class MultipleThreadsServlet extends MetricServlet {

    private static final int NUM_THREADS = 100;

    @Override
    protected void initializeData() {
        // do nothing
    }

    @Override
    protected long doWork() throws Exception {
        return startThreadsAndJoin();
    }

    public long startThreadsAndJoin() throws Exception {
        Worker[] wkers = new Worker[NUM_THREADS];
        int expected = 0;
        // create all of the threads
        for (int i = 0; i < NUM_THREADS; i++) {
            wkers[i] = new Worker(i);
            expected += i;
        }
        // start all of the threads
        for (Worker wk : wkers) {
            wk.start();
        }
        // join all of the threads
        for (Worker wk : wkers) {
            wk.join();
        }
        // add up all of the outputs
        int totalOutput = 0;
        for (Worker wk : wkers) {
            totalOutput += wk.getOutput();
        }
        if (totalOutput != expected) {
            throw new Exception("The total output is not correct " + totalOutput);
        }
        return totalOutput;
    }

    private class Worker extends Thread {

        private final int position;
        private int output = 0;

        Worker(int pPosition) {
            super();
            position = pPosition;
        }

        @Override
        public void run() {
            try {
                Thread.sleep(2);
                output = position;
            } catch (InterruptedException e) {
                output = 0;
            }

        }

        public int getOutput() {
            return output;
        }
    }

}