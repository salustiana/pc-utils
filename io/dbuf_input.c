#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define READLEN		8
#define HISTLEN		16
#define BUFLEN		(READLEN+HISTLEN)

char buf[BUFLEN];
ssize_t rb;
size_t buf_i, hist_start;

int next_char()
{
	char c = buf[buf_i++];
	buf_i %= BUFLEN;
	if (buf_i == hist_start) {
		if (buf_i + READLEN > BUFLEN)
			rb = read(STDIN_FILENO, buf+buf_i, BUFLEN-buf_i);
		else
			rb = read(STDIN_FILENO, buf+buf_i, READLEN);

		if (rb < 0) {
			perror("error reading from stdin\n");
			exit(1);
		}
		if (rb == 0)
			return 0;
		hist_start = (buf_i + rb) % BUFLEN;
	}
	return c;
}

int unread_char()
{
	if (buf_i == hist_start)
		return 1;
	--buf_i;
	buf_i %= BUFLEN;
	return 0;
}

/*
void print_buf()
{
	for (int i = 0; i < BUFLEN; i++)
		putchar(buf[i] == '\n' ? '^' : buf[i]);
	putchar('\n');
	for (int i = 0; i < buf_i; i++)
		putchar(' ');
	printf("^i\n");
	for (int i = 0; i < hist_start; i++)
		putchar(' ');
	printf("^hs\n");
}

int main()
{
	memset(buf, 'X', BUFLEN);

	rb = read(STDIN_FILENO, buf, READLEN);
	hist_start = rb;

	int look;
	while ((look = next_char()) > 0)
		printf("--- %c\n", look == '\n' ? '^' : look);
}
*/
