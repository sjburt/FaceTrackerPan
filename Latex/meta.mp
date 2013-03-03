input metauml;
beginfig(1);
    
	Activity.gui("GUI");	
	Activity.cam("Webcam");
	Activity.fd("OpenCv");
	Activity.sm("State Machine");
	Activity.usb("USB");
	Activity.control("PID");
	
	Activity.uc("uC");
	Activity.servos("Servos");
	
	Package.PC("PC")(gui,sm,control,fd,usb);
	
	leftToRight(20)(gui,sm,control);
	topToBottom(20)(fd,gui);
	topToBottom(20)(gui,cam);
	topToBottom(20)(cam,servos);
	topToBottom(20)(sm,usb);
	topToBottom(20)(usb,uc);
	
		
	drawObjects(PC,cam,servos,uc);
	
	clink(transition)(gui,fd);
	clink(transition)(fd,gui);
	clink(transition)(gui,sm);
	clink(transition)(sm,usb);
	clink(transition)(usb,uc);
	clink(transition)(sm,control);
	clink(transition)(control,sm);
	clink(transition)(uc,servos);
	clink(transition)(servos,cam);
	clink(transition)(cam,gui);
	
endfig;

beginfig(2);
	Begin.b;
	State.Init("Initialize")();
	State.WaitForFace("Wait for Face")();
	State.TrackFace("Track Face")();
	State.ScanLeft("Scan Left")();
	State.ScanRight("Scan Right")();
	State.WaitL("Short wait")();
	State.WaitR("Short wait")();
	
	Init.w = b.e + (25,0);
	WaitForFace.n = Init.s + (0,-25);
	TrackFace.n = WaitForFace.s + (0,-25);
	WaitL.ne = TrackFace.sw + (-25,-50);
	WaitR.nw = TrackFace.se + (25,-50);
	
	ScanLeft.se = WaitL.ne + (-25,25);
	ScanRight.sw = WaitR.nw +(25,25);
	
	drawObjects(b,Init,WaitForFace,TrackFace,ScanLeft,ScanRight,WaitL,WaitR);
	
	link(transition)(b.e -- Init.w);
	link(transition)(Init.s-- WaitForFace.n);
	clink(transition)(WaitForFace,TrackFace);
	clink(transition)(WaitForFace,ScanLeft);
	clink(transition)(TrackFace,WaitL);
	clink(transition)(TrackFace,WaitR);
	clink(transition)(WaitL,ScanLeft);
	clink(transition)(WaitR,ScanRight);
	clink(transition)(ScanRight,ScanLeft);
	clink(transition)(ScanLeft,ScanRight);
	
	clink(transition)(ScanRight,TrackFace);
	clink(transition)(ScanLeft,TrackFace);
endfig;


beginfig{3}

	



endfig;



end