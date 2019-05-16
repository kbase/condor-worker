#!/usr/bin/env jshell-wrapper

System.out.println("Available Processors");
System.out.println(Runtime.getRuntime().availableProcessors());

System.out.println("Free Memory");
System.out.println(Runtime.getRuntime().freeMemory() + " " + Runtime.getRuntime().freeMemory() / 1000000000 + "G");

System.out.println("Max Memory");
System.out.println(Runtime.getRuntime().maxMemory() + " " + Runtime.getRuntime().maxMemory() / 1000000000 + "G");
