package com.nr.test.servlet;

import java.rmi.server.UID;
import java.util.regex.Pattern;

public class TwoMethodsInstrumentedServlet extends MetricServlet {

    private static final Pattern PATTERN = Pattern.compile("[0-9]");

    @Override
    protected long doWork() {
        return sumEveryInteger(getUID().toString());
    }

    private long sumEveryInteger(String id) {
        long output = 0;
        char[] values = id.toCharArray();
        String charAsString;
        for (char current : values) {
            charAsString = String.valueOf(current);
            if (isNumber(charAsString)) {
                output += Integer.parseInt(charAsString);
            }
        }
        return output;
    }

    private boolean isNumber(String value) {
        return PATTERN.matcher(value).matches();
    }

    private UID getUID() {
        return new UID();
    }

    @Override
    protected void initializeData() {
    }

}