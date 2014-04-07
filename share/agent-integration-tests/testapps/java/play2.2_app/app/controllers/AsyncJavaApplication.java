package controllers;

import play.libs.F.Function;
import play.libs.F.Function0;
import play.libs.F.Promise;
import play.mvc.Controller;
import play.mvc.Result;
import views.html.index;

import com.newrelic.api.agent.Trace;

public class AsyncJavaApplication extends Controller {
    index template;

    public static Promise<Result> index() {
        Promise<Boolean> promiseOfInt = Promise.promise(new Function0<Boolean>() {
            @Override
            public Boolean apply() throws Throwable {
                someSlowMethod();
                return true;
            }
        });

        return promiseOfInt.map(new Function<Boolean, Result>() {
            @Override
            public Result apply(Boolean i) {
                return ok(index.render("Your new Play2+Java application is ready. " + i));
            }
        });
    }

    @Trace()
    public static void someSlowMethod() {
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
        }
    }
}
