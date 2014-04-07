package com.nr.test.quartz;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.quartz.CronTriggerFactoryBean;
import org.springframework.scheduling.quartz.SchedulerFactoryBean;
import org.springframework.scheduling.quartz.SpringBeanJobFactory;
import org.springframework.test.context.ContextConfiguration;

//@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = { "/applicationContext.xml" })
public class JobTest {

    @Autowired
    private SpringBeanJobFactory jobFactory;

    @Autowired
    private SchedulerFactoryBean schedulerFactory;

    @Autowired
    private CronTriggerFactoryBean trigger;

    /**
     * Quartz 1.x test
     * 
     * @throws Exception
     */
    // @Test
    // public void theJobRunsCorrectly() throws Exception {
    // this.getClass().getre
    // final TriggerFiredBundle bundle = new TriggerFiredBundle((JobDetail) trigger.getJobDataMap().get(
    // JobDetailAwareTrigger.JOB_DETAIL_KEY), trigger.getObject(), (Calendar) new CronCalendar(
    // trigger.getObject().getCronExpression()), false, new Date(), new Date(),
    // trigger.getObject().getPreviousFireTime(), trigger.getObject().getNextFireTime());
    //
    // final Job job = jobFactory.newJob(bundle);
    // job.execute(new JobExecutionContext(schedulerFactory.getScheduler(), bundle, job));
    // assertTrue(((TestJob) job).didRun());
    //
    // }

    /**
     * Quartz 2.x test
     * 
     * @throws Exception
     */
    // @Test
    // public void theJobRunsCorrectly() throws Exception {
    // final TriggerFiredBundle bundle = new TriggerFiredBundle((JobDetail) trigger.getJobDataMap().get(
    // JobDetailAwareTrigger.JOB_DETAIL_KEY), (CronTriggerImpl) trigger.getObject(),
    // (Calendar) new CronCalendar(trigger.getObject().getCronExpression()), false, new Date(), new Date(),
    // trigger.getObject().getPreviousFireTime(), trigger.getObject().getNextFireTime());
    //
    // final Job job = jobFactory.newJob(bundle);
    // job.execute(new JobExecutionContextImpl(schedulerFactory.getScheduler(), bundle, job));
    // assertTrue(((TestJob) job).didRun());
    // }
}
