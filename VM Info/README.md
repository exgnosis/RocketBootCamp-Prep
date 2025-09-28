# Rocket Bootcamp VM Info

This folder contains the setup list for the software installed in the VM for the Rocket bootcamp 

---

 
The following are installed on top of the base image provided by Protech.

### git

There was no git config in the installed version of git

The following was added as a global configuration.

```bash
git config --list
user.name=Rocket Student
user.email=noone@nowhere.com
alias.ll=log --oneline --graph --decorate --all
init.defaultbranch=main
core.editor=code --wait
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
```

- The alias just is more convenient way of showing the history of a repo that students realate to.
- It also sets VS code as the default git editor

### Java

- Java 21 open-jdk is installed.
- Confirmation

```bash
protech@studentvm:~/test$ java -version
openjdk version "21.0.8" 2025-07-15
OpenJDK Runtime Environment (build 21.0.8+9-Ubuntu-0ubuntu122.04.1)
OpenJDK 64-Bit Server VM (build 21.0.8+9-Ubuntu-0ubuntu122.04.1, mixed mode, sharing)
protech@studentvm:~/test$ javac -version
javac 21.0.8

```

### Maven

- Installed from the apt repository

```bash
rotech@studentvm:~/test/hello-world$ mvn -v
Apache Maven 3.6.3
Maven home: /usr/share/maven
Java version: 21.0.8, vendor: Ubuntu, runtime: /usr/lib/jvm/java-21-openjdk-amd64
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "6.8.0-1031-azure", arch: "amd64", family: "unix"
```

- Tested with the hello world app

```bash
mvn archetype:generate -DgroupId=com.example.helloworld \
    -DartifactId=hello-world \
    -DarchetypeArtifactId=maven-archetype-quickstart \
    -DinteractiveMode=false
```

- With the added lines to the POM file below  to use the right compiler version in the configuration section

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.11.0</version>
      <configuration>
        <source>21</source>
        <target>21</target>
      </configuration>
    </plugin>
  </plugins>
</build>

```

### Gradle

- Also installed gradle.
- To get the latest version, used sdkman!

```bash
sudo apt update
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

sdk install gradle

gradle -v

Welcome to Gradle 9.0.0!

Here are the highlights of this release:
 - Configuration Cache is the recommended execution mode
 - Gradle requires JVM 17 or higher to run
 - Build scripts use Kotlin 2.2 and Groovy 4.0
 - Improved Kotlin DSL script compilation avoidance

For more details see https://docs.gradle.org/9.0.0/release-notes.html


------------------------------------------------------------
Gradle 9.0.0
------------------------------------------------------------

Build time:    2025-07-31 16:35:12 UTC
Revision:      328772c6bae126949610a8beb59cb227ee580241

Kotlin:        2.2.0
Groovy:        4.0.27
Ant:           Apache Ant(TM) version 1.10.15 compiled on August 25 2024
Launcher JVM:  21.0.8 (Ubuntu 21.0.8+9-Ubuntu-0ubuntu122.04.1)
Daemon JVM:    /usr/lib/jvm/java-21-openjdk-amd64 (no JDK specified, using current Java home)
OS:            Linux 6.8.0-1031-azure amd64

```
- Tested with the default gradle project

```bash
protech@studentvm:~$ gradle -v

Welcome to Gradle 9.0.0!

Here are the highlights of this release:
 - Configuration Cache is the recommended execution mode
 - Gradle requires JVM 17 or higher to run
 - Build scripts use Kotlin 2.2 and Groovy 4.0
 - Improved Kotlin DSL script compilation avoidance

For more details see https://docs.gradle.org/9.0.0/release-notes.html


------------------------------------------------------------
Gradle 9.0.0
------------------------------------------------------------

Build time:    2025-07-31 16:35:12 UTC
Revision:      328772c6bae126949610a8beb59cb227ee580241

Kotlin:        2.2.0
Groovy:        4.0.27
Ant:           Apache Ant(TM) version 1.10.15 compiled on August 25 2024
Launcher JVM:  21.0.8 (Ubuntu 21.0.8+9-Ubuntu-0ubuntu122.04.1)
Daemon JVM:    /usr/lib/jvm/java-21-openjdk-amd64 (no JDK specified, using current Java home)
OS:            Linux 6.8.0-1031-azure amd64

```



### VS Code Java

- Installed the Extension Pack for Java (by Microsoft)

--- 

### C/C++  

- Installed a standard build set with multiple tools

```bash 
sudo apt install -y \
  build-essential gdb \
  clang lldb clang-tidy clang-format clangd \
  cmake ninja-build pkg-config \
  valgrind cppcheck

```

#### C Test

- Test file `hello.c`

```C
#include <stdio.h>
int main() {
    printf("Hello, C World!\n");
    return 0;
}
```
```bash
protech@studentvm:~/test$ gcc hello.c -o hello_c && ./hello_c
Hello, C World!
```

#### C++ Test

- Test file `hello.cpp`

```C++
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, C++ World!" << endl;
    return 0;
}
```

```bash
g++ hello.cpp -o hello_cpp && ./hello_cpp
Hello, C++ World!
```

---

### VS Code Extensions

- Installed the recommended extensions from MicroSoft
- C/C++ (ms-vscode.cpptools)
- C/C++ Extension Pack (optional bundle)

---

## Python

- Installed the dead snakes repo for Python 1.13

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

- Then used alternatives to set as the default Python

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.13 2
```

- And test

```bash
protech@studentvm:~$ python --version
Python 3.13.7
```

*Note: I thought about using Anaconda but I think that is way to heavyweight for this boot camp*

### VScode 

- Set up the extensions `Python (Ms-python.python)`


--- 

## Docker

- Docker is installed to support running any webservices labs we might to later. 

---

## Go 

Installed with a binary download 'go1.25.0.linux-amd64.tar.gz' from the Go website

```bash
sudo tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

protech@studentvm:~/test$ go version
go version go1.25.0 linux/amd64
```

- Used the following test file `main.go`

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}

```

```bash
protech@studentvm:~/test$ go run main.go
Hello, World!
```

- The standard GO extension pack from Google is installed in VSCode.

---

## Jenkins

- Jenkins is installed as a war file
- Start by executing `java -jar jenkins.war` in the `~/Jenkins` directory
- User name is `protech` and password is `Pa$$w0rd`
- It is also stored in the passwords area of Firefox.

# End
