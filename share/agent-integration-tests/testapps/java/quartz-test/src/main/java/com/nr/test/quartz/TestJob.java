package com.nr.test.quartz;

import org.quartz.JobExecutionContext;
import org.quartz.JobExecutionException;
import org.springframework.scheduling.quartz.QuartzJobBean;

import com.newrelic.api.agent.NewRelic;

//@DisallowConcurrentExecution
public class TestJob extends QuartzJobBean {

    private TestBean testBean;

    public TestJob() {
        System.out.println("new TestJob(): " + this);
    }

    @Override
    protected void executeInternal(final JobExecutionContext context) throws JobExecutionException {
        // System.out.println("TestJob(" + this + ").executeInternal() with TestBean(" + testBean + ")");
        // if (testBean.didRun())
        // throw new IllegalStateException("TestBean(" + testBean + ") already ran");
        try {
            testBean.run();
        } catch (Throwable e) {
            System.out.println("NOTICING ERROR");
            NewRelic.noticeError(e);
        }
    }

    public Boolean didRun() {
        return testBean.didRun();
    }

    public TestBean getBean() {
        return testBean;
    }

    public void setBean(final TestBean testBean) {
        this.testBean = testBean;
    }
}