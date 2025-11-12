#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fstream>

const int PORT = 11111;

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "Failed to create socket." << std::endl;
        return 1;
    }

    int broadcastEnable = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable)) < 0) {
        std::cerr << "Failed to set socket options." << std::endl;
        close(sock);
        return 1;
    }

    struct sockaddr_in broadcastAddr{};
    broadcastAddr.sin_family = AF_INET;
    broadcastAddr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, "255.255.255.255", &broadcastAddr.sin_addr) <= 0) {
        std::cerr << "Failed to set broadcast address." << std::endl;
        close(sock);
        return 1;
    }

    std::string intention, intention_display;
    std::cout << "Enter Intention (or Textfile): ";
    std::getline(std::cin, intention);
    intention_display = intention;
    //If intention is a textfile, read its contents into intention
    if ((intention.find(".txt")!= std::string::npos) or (intention.find(".TXT")!= std::string::npos)) {
        //if file does not exist, keep asking for the file or for a regular intention without an extension
        while (!std::ifstream(intention)) {
            std::cout << "File does not exist. Enter Intention (or Textfile): ";
            std::getline(std::cin, intention);
            intention_display = intention;
        }
        std::cout << "Reading from textfile..." << std::endl;
        std::ifstream file(intention);
        std::string line;
        while (std::getline(file, line)) {
            intention += line;
        }
        std::cout << "Finished reading." << std::endl;
    }

    std::cout << "Broadcasting: " << intention_display << "..." << std::endl;

    long i = 0;
    while (true) {
        if (i % 100000 == 0) {
            std::cout << "Intention sent " << i << " times.\r" << std::flush;
        }
        i++;
        ssize_t bytesSent = sendto(sock, intention.c_str(), intention.length(), 0,
                                   reinterpret_cast<struct sockaddr*>(&broadcastAddr),
                                   sizeof(broadcastAddr));
        if (bytesSent < 0) {
            std::cerr << "Failed to send broadcast message." << std::endl;
            break;
        }
        //sleep(1);  // Delay for 1 second between each broadcast
    }

    close(sock);
    return 0;
}