package com.nr.test.quartz;

import org.springframework.context.support.ClassPathXmlApplicationContext;

public class Main {

    public static void main(final String[] args) {
        new ClassPathXmlApplicationContext("/applicationContext.xml");
    }
}