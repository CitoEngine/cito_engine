# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "hashicorp/precise64"
  config.omnibus.chef_version = :latest
  config.vm.synced_folder ".", "/vagrant", nfs: true

  config.vm.provider "virtualbox" do |vb|
     # Keep disabled to run in headless mode
     # vb.gui = true

     # Use VBoxManage to customize the VM. For example to change memory:
     vb.customize ["modifyvm", :id, "--memory", "1024"]
  end

  config.vm.network "private_network", ip: "192.168.66.66"

  config.cache.scope = :box

  #config.vm.provision "chef_solo" do |chef|
  #  chef.cookbooks_path = "./cookbooks"
  #  chef.add_recipe  "apt"
  #  chef.add_recipe  "iptables"
  #  chef.add_recipe  "build-essential"
  #  chef.add_recipe "python"
  #end


end