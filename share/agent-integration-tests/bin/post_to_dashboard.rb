#!/usr/bin/env ruby
require 'uri'
require 'net/http'
require 'net/https'
require 'rubygems'
require 'json'


#uri = URI.parse('http://localhost:1234/data_points')
uri = URI.parse('https://agents-dashboard.herokuapp.com/data_points')
puts "Posting data to #{uri}"
http = Net::HTTP.new(uri.host, uri.port)
if uri.scheme == 'https'
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_NONE
end

File.open('/tmp/agent_metrics.txt') do |f|
  post_data = { "data_points" => [] }
  line = nil
  loop do
    100.times do |i|
      line = f.gets
      break unless line
      #Example: OneMethodInstrumentedServlet,ashley-mpb.local,2013-24-1 17:29:12 ,TomcatMetricTest,tomcat,7.0,ns,10000,0.004318,0.009329,0.057304
      servlet, computer, date, framework, server, version, iteration, time_units, duration_disabled, duration_enabled, duration_logging = line.chomp.split(",")
      the_label = server + " " + version + " at " + iteration +  " iterations in " + time_units 
      difference = "#{duration_enabled.to_f - duration_disabled.to_f}"
      post_data["data_points"].push({
        :value => duration_enabled,
        :graph_and_series_names => ["Java Agent Benchmarks - #{framework} - Agent Enabled", servlet],
        :occurred_at => date,
        :label =>  the_label
      })
      post_data["data_points"].push({
        :value => duration_logging,
        :graph_and_series_names => ["Java Agent Benchmarks - #{framework} - Agent Logging Enabled", servlet],
        :occurred_at => date,
        :label =>  the_label
      })
      post_data["data_points"].push({
        :value => difference,
        :graph_and_series_names => ["Java Agent Benchmarks - #{framework} - Agent Overhead", servlet],
        :occurred_at => date,
        :label =>  the_label
      })
    end
    request = Net::HTTP::Post.new(uri.request_uri)
    request.basic_auth("newrelic", "3mploy33")
    request.body =(post_data.to_json)
    request['Content-Type'] = 'application/json'
    request['Accepts'] = 'application/json'

    response = http.request(request)
    print "."
    break unless line
  end

end
puts
