name := "play2_2_app"

version := "1"

libraryDependencies ++= Seq(
  "com.newrelic.agent.java" % "newrelic-api" % "3.1.0",
  jdbc,
  anorm,
  cache
)

play.Project.playScalaSettings
