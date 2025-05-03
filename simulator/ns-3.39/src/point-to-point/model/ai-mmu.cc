#include "ai-mmu.h"

#include "ns3/assert.h"
#include "ns3/boolean.h"
#include "ns3/global-value.h"
#include "ns3/log.h"
#include "ns3/object-vector.h"
#include "ns3/packet.h"
#include "ns3/random-variable.h"
#include "ns3/simulator.h"
#include "ns3/uinteger.h"

#include <fstream>
#include <iostream>

#define LOSSLESS 0
#define LOSSY 1
#define DUMMY 2

#define DT 101
#define FAB 102
#define CS 103
#define IB 104
#define ABM 110
#define REVERIE 111

NS_LOG_COMPONENT_DEFINE("AiMmu");

namespace ns3
{
TypeId
AiMmu::GetTypeId(void)
{
    static TypeId tid = TypeId("ns3::AiMmu").SetParent<SwitchMmu>().AddConstructor<AiMmu>();
    return tid;
}

AiMmu::AiMmu(void)
    : SwitchMmu()
{
    NS_LOG_FUNCTION(this);
    SetUseAI(true);
}


/*modification end*/

} // namespace ns3