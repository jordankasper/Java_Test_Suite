package controllers;

import play.mvc.Controller;
import play.mvc.Result;
import views.html.index;
import com.newrelic.api.agent.NewRelic;

public class JavaApplication extends Controller {

    public static Result index() {
        return ok(index.render("Your new Play2+Java application is ready."));
    }

    public static Result hello() {
        NewRelic.setTransactionName("CustomTest", "HelloJavaTransaction");       
        return ok(index.render("HelloThere! Welcome to Play"));
    }

}
