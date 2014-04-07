# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu12_64"
  config.vm.provision :puppet, :module_path => "manifests", :manifest_file => "agent-integration-tests.pp"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "https://s3.amazonaws.com/cont-delivery-scripts/quantal64.box"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "./share", "/deploy_scripts"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. 
  config.vm.network :forwarded_port, guest: 8000, host: 18000
  config.vm.network :forwarded_port, guest: 8080, host: 18080

  # customize VM

  config.vm.provider "virtualbox" do |vb|
    vb.customize [
                        "modifyvm", :id,
                        "--memory", "4096",
                        "--name", "Test Box"
                      ]
  end
end