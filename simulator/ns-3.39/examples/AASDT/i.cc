/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "iostream"

// Default Network Topology
//
//       
//
//
//
//    point-to-point
//

/*Buffer Management Algorithms*/
# define DT 0
# define EDT 1
# define TDT 2
# define AASDT 3
# define ALPHA -3


/*switch port num*/
# define PORTNUM 8

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("experiment1");

void
Gen_Incast(uint32_t incastServer,uint16_t port,uint32_t portNum,NodeContainer& left,
            NodeContainer& right,uint32_t flowSize,Time startApp,double end_time){
  //uint32_t n = port.size();
  //Time startApp = (NanoSeconds(150) + MilliSeconds(200));
  Ptr<Node> rxNode = right.Get(incastServer);
  Ptr<Ipv4> ipv4 = rxNode->GetObject<Ipv4>();
  Ipv4InterfaceAddress rxInterface = ipv4->GetAddress(1, 0);
  Ipv4Address rxAddress = rxInterface.GetLocal();
  for(uint32_t i = 0;i < portNum;++i){
    InetSocketAddress ad(rxAddress, port);
	  Address sinkAddress(ad);
    Ptr<BulkSendApplication> bulksend = CreateObject<BulkSendApplication>();
	  bulksend->SetAttribute("Protocol", TypeIdValue(TcpSocketFactory::GetTypeId()));
	  bulksend->SetAttribute("SendSize", UintegerValue(flowSize));
	  bulksend->SetAttribute("MaxBytes", UintegerValue(flowSize));
	  bulksend->SetAttribute("Remote", AddressValue(sinkAddress));
	  bulksend->SetStartTime(startApp);
	  bulksend->SetStopTime(Seconds(end_time));
    left.Get(i)->AddApplication(bulksend);

    PacketSinkHelper sink("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), port++));
	  ApplicationContainer sinkApp = sink.Install(right.Get(incastServer));
	  sinkApp.Start(startApp);
	  sinkApp.Stop(Seconds(end_time));
  }
}

void 
Gen_Longflow(uint16_t port,uint32_t portNum,NodeContainer& left,
                NodeContainer& right,uint32_t flowSize,double end_time){
  Time startApp = (NanoSeconds(150) + MilliSeconds(200));
  for(uint32_t i = 0;i < portNum;++i){
    Ptr<Node> rxNode = right.Get(i);
    Ptr<Ipv4> ipv4 = rxNode->GetObject<Ipv4>();
    Ipv4InterfaceAddress rxInterface = ipv4->GetAddress(1, 0);
    Ipv4Address rxAddress = rxInterface.GetLocal();
    InetSocketAddress ad(rxAddress, port);
	  Address sinkAddress(ad);
    Ptr<BulkSendApplication> bulksend = CreateObject<BulkSendApplication>();
	  bulksend->SetAttribute("Protocol", TypeIdValue(TcpSocketFactory::GetTypeId()));
	  bulksend->SetAttribute("SendSize", UintegerValue(flowSize));
	  bulksend->SetAttribute("MaxBytes", UintegerValue(flowSize));
	  bulksend->SetAttribute("Remote", AddressValue(sinkAddress));
	  bulksend->SetStartTime(startApp);
	  bulksend->SetStopTime(Seconds(end_time));
    left.Get(i)->AddApplication(bulksend);

    PacketSinkHelper sink("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), port++));
	  ApplicationContainer sinkApp = sink.Install(right.Get(i));
	  sinkApp.Start(startApp);
	  sinkApp.Stop(Seconds(end_time));  
  }
                
}

int
main (int argc, char *argv[])
{
  CommandLine cmd (__FILE__);
  cmd.Parse (argc, argv);
  
  Time::SetResolution(Time::NS);
  //LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
  //LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);

  uint32_t flowSize = 1800000;
  uint32_t BUFFERSIZE = 9*1000*1000;
  uint32_t LEFTNUM = 32;//32
  uint32_t RIGHTNUM = 4;
  double end_time = 20;


  NodeContainer leftNodes;
  leftNodes.Create(LEFTNUM);
  NodeContainer switchNodes;
  switchNodes.Create(PORTNUM);
  NodeContainer rightNodes;
  rightNodes.Create(RIGHTNUM);

  //int strategy = DT; 
  //int strategy = EDT; 
  int strategy = TDT; 
  //int strategy = AASDT; 

  // init ptr
  Ptr<UintegerValue> m_PortNumPtr = Create<UintegerValue>(PORTNUM);;
  Ptr<UintegerValue> m_usedBufferPtr = Create<UintegerValue>(0);
  Ptr<UintegerValue> m_stateChangePtr = Create<UintegerValue>(1);

  for(uint32_t i = 0;i < switchNodes.GetN();++i){
    Ptr<Node> node = switchNodes.Get(i);
    node->SetNodeType(1);
    node->m_switch->SetStrategy(strategy);
    node->m_switch->SetPort(i);
    //std::cout<<node->m_switch->GetPort()<<std::endl;
    node->m_switch->SetdtAlphaExp(ALPHA);
    node->m_switch->SetdtInitialAlphaExp(ALPHA);
    node->m_switch->SetSharedBufferSize(BUFFERSIZE);
    node->m_switch->SetUsedBufferPtr(m_usedBufferPtr);
    node->m_switch->SetPortNumPtr(m_PortNumPtr);
    node->m_switch->SetStateChangePtr(m_stateChangePtr);
  }

  if(strategy == DT){
    std::cout<<"--------- this is DT strategy ---------"<<std::endl;
  }else if(strategy == EDT){
    std::cout<<"--------- this is EDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_EDTCPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_EDTNCPortNumPtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetEDTPortNumPtr(m_EDTCPortNumPtr,m_EDTNCPortNumPtr);
    }
  }else if(strategy == TDT){
    std::cout<<"--------- this is TDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_TDTNPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_TDTAPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_TDTEPortNumPtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetTDTPortNumPtr(m_TDTNPortNumPtr,m_TDTAPortNumPtr,m_TDTEPortNumPtr);
    }
  }else if(strategy == AASDT){
    std::cout<<"--------- this is AASDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_AASDTNPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_AASDTIPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCIPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCCPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTITimePtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCTimePtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetAASDTPortNumPtr(m_AASDTNPortNumPtr,m_AASDTIPortNumPtr,m_AASDTCPortNumPtr,m_AASDTCIPortNumPtr,m_AASDTCCPortNumPtr);
      node->m_switch->SetAASDTICNumPtr(m_AASDTITimePtr,m_AASDTCTimePtr);
    }
    //Simulator::Schedule(Seconds(1), &(sw->m_switch->AASDTReset));
  }else{
    std::cout<<"--------- strategy error ---------"<<std::endl;
  }


  InternetStackHelper internet;
	Ipv4GlobalRoutingHelper globalRoutingHelper;
	internet.SetRoutingHelper(globalRoutingHelper);
  internet.Install(leftNodes);
  internet.Install(switchNodes);
  internet.Install(rightNodes);

  PointToPointHelper pointToPoint;
  Ipv4AddressHelper ipv4;
  Ipv4InterfaceContainer ls[LEFTNUM][PORTNUM];
  Ipv4InterfaceContainer sr[PORTNUM][RIGHTNUM];

  //l <--> s
  ipv4.SetBase("10.1.0.0", "255.255.252.0");
  pointToPoint.SetDeviceAttribute("DataRate", StringValue ("10Gbps"));
  pointToPoint.SetChannelAttribute("Delay", StringValue ("10ms"));
  //pointToPoint.SetQueue("ns3::DropTailQueue", "MaxSize", StringValue("10p"));
  //pointToPoint.SetQueue("ns3::DropTailQueue","MaxSize",QueueSizeValue(QueueSize(QueueSizeUnit::BYTES,2000)));
  for(uint32_t left = 0;left < LEFTNUM;++left){
    //ipv4.NewNetwork();
    //for(uint32_t s = 0;s < PORTNUM;++s){
    for(uint32_t s = 0;s < 3;++s){
      NodeContainer nodeContainer = NodeContainer(leftNodes.Get(left), switchNodes.Get(s));
      NetDeviceContainer netDeviceContainer = pointToPoint.Install(nodeContainer);
      ls[left][s] = ipv4.Assign(netDeviceContainer);
      //ls[left][s] = ipv4.Assign(netDeviceContainer.Get(1));
      //ipv4.Assign(netDeviceContainer.Get(0));
    }
  }

  //s <--> r
  ipv4.SetBase("10.2.0.0", "255.255.252.0");
  pointToPoint.SetDeviceAttribute("DataRate", StringValue ("10Gbps"));
  pointToPoint.SetChannelAttribute("Delay", StringValue ("10ms"));
  //pointToPoint.SetQueue("ns3::DropTailQueue","MaxSize",QueueSizeValue(QueueSize(QueueSizeUnit::BYTES,2000)));
  for(uint32_t s = 0;s < 3;++s){
  //for(uint32_t s = 0;s < PORTNUM;++s){
    NodeContainer nodeContainer = NodeContainer(switchNodes.Get(s),rightNodes.Get(s));
    NetDeviceContainer netDeviceContainer = pointToPoint.Install(nodeContainer);
    sr[s][s] = ipv4.Assign(netDeviceContainer);
    //ipv4.NewNetwork();
    /* for(uint32_t right = 0;right < RIGHTNUM;++right){
      NodeContainer nodeContainer = NodeContainer(switchNodes.Get(s),rightNodes.Get(right));
      NetDeviceContainer netDeviceContainer = pointToPoint.Install(nodeContainer);
      sr[s][right] = ipv4.Assign(netDeviceContainer);
      //sr[s][right] = ipv4.Assign(netDeviceContainer.Get(1));
      //ipv4.Assign(netDeviceContainer.Get(0));
    } */
  }

//---------------------------------TCP----------------------------------------
  uint32_t portNUM = 32;
  Time startApp = (NanoSeconds(150) + MilliSeconds(200));

  uint16_t port1 = 50000;
  uint32_t incastServer1 = 0;
  Gen_Incast(incastServer1,port1,portNUM,leftNodes,rightNodes,flowSize,startApp,end_time);

  uint16_t port2 = 40000;
  uint32_t incastServer2 = 1;
  Gen_Incast(incastServer2,port2,portNUM,leftNodes,rightNodes,flowSize,startApp,end_time);

  /* uint16_t port3 = 30000;
  uint32_t incastServer3 = 2;
  Gen_Incast(incastServer3,port3,portNUM,leftNodes,rightNodes,flowSize,startApp,end_time); */

/*   uint16_t port1 = 40000;
  Gen_Longflow(port1,4,leftNodes,rightNodes,flowSize,end_time); */


//----------------------------------------------------------------------------

  // Flow monitor
  Ptr<FlowMonitor> flowMonitor;
  FlowMonitorHelper flowHelper;
  flowMonitor = flowHelper.InstallAll();
  

  Ipv4GlobalRoutingHelper::PopulateRoutingTables();
  Simulator::Stop(Seconds(end_time));
  Simulator::Run();

  flowMonitor->SerializeToXmlFile("flow-monitor3.xml", true, true);
  Simulator::Destroy();
  return 0;
}
