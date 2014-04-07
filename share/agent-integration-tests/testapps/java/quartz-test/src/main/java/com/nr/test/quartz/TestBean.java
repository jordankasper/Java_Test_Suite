package com.nr.test.quartz;

public class TestBean {

    private Boolean ran = false;

    public void run() {
        ran = true;
    }

    public Boolean didRun() {
        return ran;
    }

}