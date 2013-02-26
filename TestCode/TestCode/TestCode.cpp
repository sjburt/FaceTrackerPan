// TestCode.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "stdio.h"
#include <time.h>
#include <stdlib.h>
#include <string.h>

void clean_string( char* clean,const char* dirty)
{
	unsigned int cleanidx = 0;
	unsigned int dirtyidx = 0;

	while(dirty[dirtyidx++]==0x7F);

	while(dirty[dirtyidx++-1]!=0x7F)
	{
		if (dirty[dirtyidx-2]==0x7E)
		{
			clean[cleanidx++]=((dirty[dirtyidx-1]) ^ (0x20));
			dirtyidx++;
		}
		else
		{
			clean[cleanidx++]=dirty[dirtyidx-2];
		}
	}
	clean[cleanidx] = '\0';
}

void dirty_string( char* dirty, const  char *clean)
{
	unsigned int cleanidx =0;
	unsigned int dirtyidx =0;

	dirty[dirtyidx++] = 0x7F;
	while(clean[cleanidx++] != '\0')
	{
		if (clean[cleanidx-1] == 0x7F)
		{	dirty[dirtyidx++] = 0x7E;
		dirty[dirtyidx++] = 0x7F ^ 0x20;
		}
		else if (clean[cleanidx-1] == 0x7E)
		{	dirty[dirtyidx++] = 0x7E;
		dirty[dirtyidx++] = 0x7E ^ 0x20;
		}
		else
		{
			dirty[dirtyidx++]=clean[cleanidx-1];
		}		
	}
	dirty[dirtyidx] = 0x7F;	
	dirty[dirtyidx+1] = '\0';
}




int _tmain(int argc, _TCHAR* argv[])
{

	char clean[1000];
	char dirty[2000];
	char cleaned[1000];
	long int j;
	srand(time(NULL));

	for (j=0; j<10000000 ; j++)
	{
		int r = 750;
		int i;
		for (i = 0; i<r;i++)
		{
			clean[i] = rand() %256;
		}
		clean[i+1] = 0x00;

		dirty_string(dirty,clean);
		clean_string(cleaned,dirty);

		if ( strcmp(clean,cleaned) != 0)
		{
			printf("Error: %s \n",clean);
			
			dirty_string(dirty,clean);
			clean_string(cleaned,dirty);
		}
	if (j%100000 == 0)	printf("%d: %s \n",j,clean);
	}






	return 0;
}

