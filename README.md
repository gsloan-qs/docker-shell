# docker-shell

A deployment type Shell for CloudShell apps. 
* **src** The docker host driver, this driver contains all relevant logic for deploying and managing the container lifecycle
* **scripts** A python script for the Docker Image deployment type, simply invokes the relevant operations on the driver
* **DataModel** The relevant attributes, structure and metadata for representing Docker Hosts and deployment parameters

## Installation

### Configuring a new Host

1. Get CloudShell free SDK and install using the installation instructions. Open the CloudShell Portal.
2. Import dockerShell.zip published in the latest release into CloudShell via Admin -> import Package
3. Navigate to the Inventory tab and click on the 'add new' link
4. Enter a name and provide the full IP address and port of the Docker Host (e.g http://55.44.2.3:4000 )
5. In the next page, optionally provide the private IP of the container if hosted under amazon or other cloud provider
6. If the host is a swarm host, repeat steps 1-5 to add the different nodes

### Create a new app with a docker image Deployment Type
1. Navigate to the 'Manage Tab' on the CloudShell Portal
2. Select Apps and click the 'Add' link
3. Select the 'Docker Image' deployment type and enter a name for the app
4. Fill in the following mundatory fields: 
  * Docker Host - The name of the docker resource you configured in the previous steps
  * Docker Image - The image to create the app container from
5. Optionally fill in the following fields:
  * Container Env - Environment variables to set for the container. Use comma separated name=vlaue syntax. E.g: **MYSQL_RANDOM_ROOT_PASSWORD=yes,MYSQL_ONETIME_PASSWORD=yes**
  * Container Ports - Additional ports to expose on the container in addition to those declared in the image
6. Click on 'Settings' and add the app to the default 'Applications' category.
7. Click 'Done'

### Deploy the app to a sandbox
1. Create a new sandbox
2. Click on +Apps/Services
3. Select the App you've created in the previous step or a different app with docker deployment configured
4. Hover on the app component and select the '>' icon representing 'commands' from the radial menu
5. Run the 'Deploy App' command 

## Build
1. Download the latest [ShellFoundry](https://github.com/QualiSystems/shellfoundry) release 
2. Make open the repo folder in your preferred Python IDE
3. After making changes, run ShellFoundry Package to create a new shell
4. Import the Shell to CloudShell to test the changes

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


