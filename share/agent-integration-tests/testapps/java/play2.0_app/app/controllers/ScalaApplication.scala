package controllers

import play.api._
import play.api.mvc._
import com.newrelic.api.agent.NewRelic;

object ScalaApplication extends Controller {

  def index = Action { request =>
    Ok(views.html.index("Your new Play2+Scala application is ready."))
  }

  def hello = Action { request =>
        NewRelic.setTransactionName("CustomTest", "HelloScalaTransaction");
        Ok(views.html.index("HelloThere! Welcome to Play"))
    }
  
  def timeout = Action { request =>
    // needs implementation
    Ok(views.html.index("Your new Play2+Scala application is ready."))
  }

}
