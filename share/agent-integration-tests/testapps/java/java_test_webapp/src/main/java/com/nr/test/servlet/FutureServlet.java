package com.nr.test.servlet;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class FutureServlet extends MetricServlet {

    private static final int NUMBER = 50;
    private static final Random RAND_GENERATOR = new Random();
    private final ThreadPoolExecutor execute = new ThreadPoolExecutor(2, 2, 1000, TimeUnit.SECONDS,
            new ArrayBlockingQueue<Runnable>(10));

    @Override
    protected void initializeData() {
        // do nothing here
    }

    @Override
    protected long doWork() throws Exception {
        return performCalculations();
    }

    private long performCalculations() throws Exception {

        Calculations cals = new Calculations();
        Future<Results> future = execute.submit(cals);
        Results res = future.get();
        return res.getValue();

    }

    class Results {
        private final long value;

        Results(long pValue) {
            value = pValue;
        }

        public long getValue() {
            return value;
        }
    }

    private class Calculations implements Callable<Results> {

        public Results call() throws Exception {
            List<Integer> factors = new ArrayList<Integer>();
            // we are just excluding 0
            for (int i = 1; i <= NUMBER; i++) {
                if ((NUMBER % i) == 0) {
                    factors.add(Integer.valueOf(i));
                }
            }
            int index = RAND_GENERATOR.nextInt(factors.size());
            Results res = new Results(factors.get(index));
            return res;
        }
    }
}