package controllers;

import java.util.concurrent.Callable;

import play.libs.Akka;
import play.libs.F.Function;
import play.libs.F.Promise;
import play.mvc.Controller;
import play.mvc.Result;
import views.html.index;

import com.newrelic.api.agent.Trace;

public class AsyncJavaApplication extends Controller {
    index test;

    public static Result index() {
        Promise<Boolean> promiseOfInt = Akka.future(new Callable<Boolean>() {
            public Boolean call() {
                someSlowMethod();
                return true;
            }
        });
        return async(promiseOfInt.map(new Function<Boolean, Result>() {
            public Result apply(Boolean i) {
                return ok(index.render("Your new Play2+Java application is ready. " + i));
            }
        }));
    }

    @Trace()
    public static void someSlowMethod() {
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
        }
    }

    // public static Result index() {
    // Promise<Response> resp = WS.url("http://newrelic.com").get();
    //
    // return async(resp.map(new Function<Response, Result>() {
    //
    // @Override
    // public Result apply(Response i) throws Throwable {
    // return ok(index.render("Your new Play2+Java application is ready: " + i.getStatus()));
    // }
    //
    // }));
    // }
}
