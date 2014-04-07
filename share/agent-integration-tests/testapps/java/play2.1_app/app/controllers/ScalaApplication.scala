package controllers

import scala.concurrent.Future
import play.api.libs.concurrent.Execution.Implicits.defaultContext
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
    val futureInt = Future {
      Thread.sleep(1000)
      1
    }
    val futureTimeout = play.api.libs.concurrent.Promise.timeout("Oops", 10000)

    Async {
      Future.firstCompletedOf(Seq(futureInt, futureTimeout)).map {
        case i: Int => Ok("Your application is ready")
        case t: String => Ok("Your application is not ready")
      }
    }
  }

}
