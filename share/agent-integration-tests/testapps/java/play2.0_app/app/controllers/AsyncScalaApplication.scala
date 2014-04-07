package controllers

import play.api.Play.current
import play.api.libs.concurrent.Akka
import play.api.mvc.Action
import play.api.mvc.Controller

object AsyncScalaApplication extends Controller {

  def index = Action { request =>
    val futureInt = Akka.future {
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