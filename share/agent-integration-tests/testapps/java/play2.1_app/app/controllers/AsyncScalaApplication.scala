package controllers

import scala.concurrent.Future
import play.api.libs.concurrent.Execution.Implicits.defaultContext
import play.api.mvc.Action
import play.api.mvc.Controller
import play.api.libs.ws.WS
import scala.util.Success
import scala.concurrent.Promise

object AsyncScalaApplication extends Controller {

  def index = Action { request =>
    val futureInt = scala.concurrent.Future {
      val sleepTime = 10
      Thread.sleep(sleepTime)
      sleepTime
    }

    Async {
      futureInt.map(i => Ok(views.html.index("Your new Play2+Scala application is ready: " + i)))
    }
  }

  //  def index = Action { request =>
  //    val resp = WS.url("http://newrelic.com").get()
  //
  //    Async {
  //      resp.map(i => Ok(views.html.index("Your new Play2+Scala application is ready: " + i.status)))
  //    }
  //  }
}