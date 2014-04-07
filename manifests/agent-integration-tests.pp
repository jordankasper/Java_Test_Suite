stage {'machine_init':}
stage {'python_installs':}
stage {'git_fetch':}
stage {'configure_tests':}
stage {'run_tests':}

Stage['machine_init'] -> Stage['python_installs'] -> Stage['git_fetch'] -> Stage['configure_tests'] -> Stage['run_tests']

#
# This Puppet script is used to regenerate the VM in the "local VM" case, i.e. not under Jenkins
# Regeneration of the VM only occurs if the local user (developer) manually deletes the old VM.
#

exec { 'apt-get update':
  command => '/usr/bin/apt-get update',
  require => File["/home/jenkins/java_agent"]
}

package { "curl":
  ensure => present,
}

package { "realpath":
  ensure => present,
}

package { "python3":
  ensure => present,
  require => Exec['apt-get update']
}

package { "unzip":
  ensure => present,
}

# Create the jenkins user
user { 'jenkins':
  ensure     => present,
  managehome => true,
  shell      => '/bin/bash',
}

file {'/home/jenkins/.bashrc' :
  source => "/deploy_scripts/jenkins_user_bashrc",
  owner => 'jenkins',
  group => 'jenkins',
  mode => 0644
}

file {'/home/jenkins/.profile' :
  source => "/deploy_scripts/jenkins_user_profile",
  owner => 'jenkins',
  group => 'jenkins',
  mode => 0644
}

# Adds jenkins' ssh key to the authorized keys file
ssh_authorized_key {'jenkins_ssh_key':
  key  => 'AAAAB3NzaC1kc3MAAACBAOC+I4HJzVPemiN3wcTWZb5KzgeCfviwG6diVUAEdlwkYiFREqmXtV+O/UMK5jQueFNVNWfn2ZkXa783nc9lHcAltQo6erYA5CDC9E09xNaC8OXkZVCqjvxQ1m2pFlNQFxeoXCB/DdanJtl3EWgLRpGA+g4Tr0Q6Fm1V1XdsjhwNAAAAFQCKJzjJEonvM+QYmgWwuT6FsuZSaQAAAIEAil3e35a+T9oGKXxU5ptgO9Kda6Eymp6G5PfCC1zvHAGSgSM2SPWWG2AumSiELkUzcqjrZt5MV4ZPbv0F7Tpw2c5F9C0elQLlVx4wyJev5ebfIQkfIqA9oqScPHHR6S9KnYolChYm+/EPD97+aK2YD1OG8uLTW8uheGJ3gmbIJFYAAACBAMHn/Io5d0nGOjm9B32OzER8dQD5LX3RjCR7rdSCnzK1lbeG4wyoVV+6LSoBkg8rdKEgn1Y6g8qnGnzmmKEuWeiAUv9d7DXa7fFYmwOehp3uusS0AEcQUFHaoQ6Wgq/vEGgS9Cf2Q6mnHf7/ykmmbyhYPd+fBPX1mMNWKTRWuets',
  type => 'dsa',
  user => 'jenkins'
}

file {'/home/jenkins/java_agent' :
  ensure => directory,
  owner => 'jenkins',
  mode => 0744,
  require => File['/home/jenkins/.profile']
}

exec {'python-yaml' :
command => "/bin/sh /deploy_scripts/curl-python3.sh > /tmp/python-distribute.out && /usr/bin/touch /home/vagrant/python-yaml-complete",
  user => 'root',
  creates => "/home/vagrant/python-yaml-complete",
  require => Package['python3']
}

exec {'environment-complete' :
  command => "/bin/sh /deploy_scripts/finalize-environment.sh && /usr/bin/touch /home/jenkins/env-setup-complete",
  user => 'root',
  cwd => "/home/jenkins/java_agent",
  creates => ['/home/jenkins/env-setup-complete'],
  require => [Package['unzip'], Exec["python-yaml"]]
}

file {'/home/jenkins/apps' :
  ensure => "directory",
  mode => 0744,
  owner => 'jenkins',
  require => Exec['environment-complete']
}

# allow use of the vagrant ssh authorization to ssh in as the jenkins user.  Used by the java_agent ant build target
# that runs automated unit tests (2014-01-15 jberkowitz: is this still true!?)
exec {'jenkins-allow-ssh':
  command => "/bin/cat /home/vagrant/.ssh/authorized_keys >> /home/jenkins/.ssh/authorized_keys && /usr/bin/touch /home/jenkins/.ssh-key-set",
  user => 'root',
  creates => '/home/jenkins/.ssh-key-set',
  require => Ssh_authorized_key ['jenkins_ssh_key']
}
