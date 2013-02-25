/*
 * simpleserial.h
 *
 * Created: 2/24/2013 10:25:52 PM
 *  Author: Steve
 */ 


#ifndef SIMPLESERIAL_H_
#define SIMPLESERIAL_H_

typedef enum SerMsg {
	NULL = 0,
	POS  = 1,
	STOP = 2,
	
	} SerMsg;


char initSerial(uint16_t baud); // Returns 0 if we got the port going. Halts if we didn't.
char handshake();  // Returns 0 if handshake succeeded
char getMessage(SerMsg *msg,uint16_t *data);



#endif /* SIMPLESERIAL_H_ */