#include <iostream>
#include <string>
#include <stdio.h>
#include <cstring>

using namespace std;

void print_help()
{
  cout << "Digital Buddhist Prayer Wheel v1.0 by Anthro Teacher." << endl;
  cout << "Optional Flag:" << endl;
  cout << " a) --help or -h" << endl;
  cout << " b) --mantra or -m, example: --mantra \"Om Mani Padme Hum\"" << endl;
  cout << " --help = Display this help." << endl;
  cout << " --mantra = The mantra to repeat, with quotes." << endl;

  cout << "Forum: https://forums.intentionrepeater.com" << endl;
  cout << "Website: https://www.intentionrepeater.com" << endl
       << endl;
}

int main(int argc, char **argv)
{
  std::string mantra, param_mantra = "";

  for (int i = 1; i < argc; i++)
  {
    if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help"))
    {
      print_help();
      exit(EXIT_SUCCESS);
    }
    else if (!strcmp(argv[i], "-m") || !strcmp(argv[i], "--mantra"))
    {
      param_mantra = argv[i + 1];
    }
  }

  cout << "Digital Buddhist Prayer Wheel v1.0 by Anthro Teacher." << endl;
  cout << "Press Ctrl-C to Exit." << endl
       << endl;

  if ((param_mantra) == "")
  {
    cout << "Mantra: ";
    std::getline(std::cin, mantra);
  }
  else
  {
    mantra = param_mantra;
  }

  while (true)
  {                                   // Loop indefinitely
    std::cout << mantra << std::endl; // Recite the mantra
  }

  return 0;
}