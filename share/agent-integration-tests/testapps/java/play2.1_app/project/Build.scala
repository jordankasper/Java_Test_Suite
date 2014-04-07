import sbt._
import Keys._
import play.Project._

object ApplicationBuild extends Build {

  val appName = "play2_1_app"
  val appVersion = "1"

  val appDependencies = Seq(
    // Add your project dependencies here,
    "com.newrelic.agent.java" % "newrelic-api" % "2.16.0",
    jdbc,
    anorm
  )

  val main = play.Project(appName, appVersion, appDependencies).settings(
    // Add your own project settings here
  )
}
