![pheonix logo](/assets/transparent_logo.png)
# Welcome to Pheonix! 
## Intended usecase and scope  

This project covers the electronics and software of a university group project for the course "Praktikum Mechatronische Systeme SS24" at the <a href = https://www.fau.de/>FAU Erlangen Nürnberg. </a>
The project scope can be described as. 
### **Scope definition:** 
The main three goals to achieve were set as: 
<strong>
1. Unit must be able to take on a payload of more than 200ml (the more the better). 
2. Unit must be able to recognise the source of a forrest fire and localize as well as transmit its position (Fire is simulated by an <a href=https://april.eecs.umich.edu/software/apriltag>AprilTag</a>). 
3. Unit must be able to deploy the palyoad release mechanism in a way most closest to the source of the flame. 
</strong>


## Installation 
This project is meant to run on Raspbian, a light-weight Debian Distribution.   

**1. Clone this Repo:**  
`$ git clone https://github.com/johabeere/phoenix`  
**2. Execute the install script with root priviliges:**  
`cd ./phoenix & sudo install.sh`

## Usage
You can run the application by calling the `start.sh` script located under `software/`:   
`$ cd software && ./start.sh`

For more information, see the respective subsections: 
* [Software](./software/SOFTWARE.md) 
* [Electronics](/electronics/ELECTRONICS.md)
* [Mechanics](./mechanics/MECHANICS.md)

## Contributors: 
The following students contributed to this project: 
### Sub-Team Mechanics: 
*   Fabian Rosenberger
*   Maéva Leplat
*   Alexander Diel
*   Julian Stracke
### Sub-Team Electronics: 
*   Mahdi Elezzi
*   Iheb Fahem
### Sub-Team Software:
*   Johannes Schraml
*   Dominique Thummerer
*   Thomas Müller
#### Thanks also goes to the two university chairs that supported our work: 
* <a href=https://www.faps.fau.de/>Lehrstuhl für Fertigungsautomatisierung und Produktionssystematik</a>
* <a href=https://www.asm.tf.fau.de/>Lehrstuhl für Autonome Systeme und Mechatronik</a>

## Disclamer and License
This is a one-time project and will lose support once it is completed. It is by no means perfect, so if you decide to replicate or use part of this project, you do so on your own risk.   
That being said, we do encourage you to reuse anything that seems usefull.   
This project is licensed under the **---INSERT LICENSE HERE---** License, for details, see <a href=https://google.com>here</a>