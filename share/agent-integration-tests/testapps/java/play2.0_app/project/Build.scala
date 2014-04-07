import sbt._
import Keys._
import PlayProject._

object ApplicationBuild extends Build {

    val appName         = "play2.0_app"
    val appVersion      = "1"

    val appDependencies = Seq(
      // Add your project dependencies here,
      "com.newrelic.agent.java" % "newrelic-api" % "2.16.0"
    )

    val main = PlayProject(appName, appVersion, appDependencies, mainLang = SCALA).settings(
      // Add your own project settings here      
    )

}
