grails.servlet.version = '2.5'
grails.project.work.dir = 'target'
grails.project.target.level = 1.6
grails.project.source.level = 1.6

grails.tomcat.jvmArgs = ["-server", "-javaagent:/Users/ashley/newrelic/java_agent/core/dist/newrelic.jar"]

grails.project.dependency.resolution = {

	inherits 'global'
	log 'error'
	checksums true
        

	repositories {
		inherits true

		grailsPlugins()
		grailsHome()
		grailsCentral()

		mavenLocal()
		mavenCentral()
	}

	dependencies {}

	plugins {
		runtime ":hibernate:$grailsVersion"
		runtime ':jquery:1.8.0'
		runtime ':resources:1.1.6'
		build ":tomcat:$grailsVersion"
		runtime ':database-migration:1.1'
		compile ':cache:1.0.0'
	}
}
