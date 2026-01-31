import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Send, 
  ArrowLeft,
  Droplets,
  MapPin,
  Phone,
  Star,
  Clock,
  CheckCheck,
  Truck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ChatMessage, PipaProvider } from '@/types';
import { mockProviders } from '@/data/mockData';
import { cn } from '@/lib/utils';

type ChatState = 
  | 'welcome' 
  | 'main_menu' 
  | 'request_location' 
  | 'show_providers' 
  | 'confirm_order'
  | 'order_confirmed'
  | 'report_type'
  | 'report_location'
  | 'report_duration'
  | 'report_affected'
  | 'report_confirmed'
  | 'prices_location'
  | 'show_prices';

const mainMenuOptions = [
  { id: '1', label: '💧 Pedir agua (pipa)' },
  { id: '2', label: '⚠️ Reportar un problema' },
  { id: '3', label: '💰 Ver precios en mi zona' },
  { id: '4', label: '📦 Mis pedidos' },
];

const reportTypes = [
  { id: '1', label: '💧 Fuga de agua' },
  { id: '2', label: '🚱 Sin agua en mi colonia' },
  { id: '3', label: '⚠️ Agua contaminada' },
  { id: '4', label: '🔧 Daño a infraestructura' },
];

const durationOptions = [
  { id: '1', label: 'Hoy' },
  { id: '2', label: '1-3 días' },
  { id: '3', label: 'Más de 3 días' },
];

export default function CitizenChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [chatState, setChatState] = useState<ChatState>('welcome');
  const [selectedProvider, setSelectedProvider] = useState<PipaProvider | null>(null);
  const [reportData, setReportData] = useState<{
    type?: string;
    duration?: string;
    affected?: number;
  }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initial greeting
    setTimeout(() => {
      addBotMessage('¡Hola! 👋 Soy AquaHub, tu asistente de servicios de agua.');
      setTimeout(() => {
        addBotMessage('¿En qué te puedo ayudar hoy?', mainMenuOptions);
        setChatState('main_menu');
      }, 500);
    }, 500);
  }, []);

  const addBotMessage = (content: string, options?: { id: string; label: string }[]) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      role: 'bot',
      content,
      timestamp: new Date(),
      options: options?.map(o => ({ id: o.id, label: o.label, value: o.id })),
    };
    setMessages(prev => [...prev, message]);
  };

  const addUserMessage = (content: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  };

  const handleOptionClick = (optionId: string, optionLabel: string) => {
    addUserMessage(optionLabel);
    processUserInput(optionId);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    addUserMessage(inputValue);
    processUserInput(inputValue);
    setInputValue('');
  };

  const processUserInput = (input: string) => {
    const lowerInput = input.toLowerCase();

    switch (chatState) {
      case 'main_menu':
        if (input === '1' || lowerInput.includes('pedir') || lowerInput.includes('agua')) {
          setTimeout(() => {
            addBotMessage('📍 Comparte tu ubicación para encontrar pipas cerca de ti.\n\nPuedes escribir tu colonia o dirección.');
            setChatState('request_location');
          }, 500);
        } else if (input === '2' || lowerInput.includes('reportar') || lowerInput.includes('problema')) {
          setTimeout(() => {
            addBotMessage('¿Qué tipo de problema quieres reportar?', reportTypes);
            setChatState('report_type');
          }, 500);
        } else if (input === '3' || lowerInput.includes('precios')) {
          setTimeout(() => {
            addBotMessage('📍 ¿En qué zona quieres ver los precios?\n\nEscribe tu colonia o dirección.');
            setChatState('prices_location');
          }, 500);
        } else if (input === '4' || lowerInput.includes('pedidos')) {
          setTimeout(() => {
            addBotMessage('📦 No tienes pedidos activos en este momento.\n\n¿Te gustaría pedir agua?', [
              { id: 'yes', label: 'Sí, pedir agua' },
              { id: 'no', label: 'Volver al menú' },
            ]);
          }, 500);
        } else {
          setTimeout(() => {
            addBotMessage('No entendí tu mensaje. ¿En qué te puedo ayudar?', mainMenuOptions);
          }, 500);
        }
        break;

      case 'request_location':
      case 'prices_location':
        setTimeout(() => {
          addBotMessage(`📍 Ubicación recibida: ${input}\n\nBuscando pipas disponibles...`);
          setTimeout(() => {
            showProviders();
          }, 1000);
        }, 500);
        break;

      case 'show_providers':
        const providerNum = parseInt(input);
        if (providerNum >= 1 && providerNum <= mockProviders.filter(p => p.available).length) {
          const provider = mockProviders.filter(p => p.available)[providerNum - 1];
          setSelectedProvider(provider);
          setTimeout(() => {
            addBotMessage(
              `Has seleccionado:\n\n🚛 ${provider.name}\n💰 $${provider.pricePerLiter}/10,000L\n⏱️ Llega en ~${provider.estimatedArrival} min\n\n¿Confirmas el pedido?`,
              [
                { id: 'confirm', label: '✅ Confirmar pedido' },
                { id: 'cancel', label: '❌ Cancelar' },
              ]
            );
            setChatState('confirm_order');
          }, 500);
        }
        break;

      case 'confirm_order':
        if (input === 'confirm' || lowerInput.includes('confirmar') || lowerInput.includes('sí')) {
          setTimeout(() => {
            const orderId = `AH-${Date.now().toString().slice(-6)}`;
            addBotMessage(
              `✅ ¡Pedido confirmado!\n\n📋 Número de pedido: #${orderId}\n🚛 Proveedor: ${selectedProvider?.name}\n💰 Total: $${selectedProvider?.pricePerLiter}\n⏱️ Tiempo estimado: ~${selectedProvider?.estimatedArrival} min\n\nTe notificaremos cuando el pipa esté en camino. 🚚`
            );
            setChatState('order_confirmed');
            setTimeout(() => {
              addBotMessage('¿Hay algo más en lo que te pueda ayudar?', mainMenuOptions);
              setChatState('main_menu');
            }, 2000);
          }, 500);
        } else {
          setTimeout(() => {
            addBotMessage('Pedido cancelado. ¿En qué más te puedo ayudar?', mainMenuOptions);
            setChatState('main_menu');
          }, 500);
        }
        break;

      case 'report_type':
        const reportTypeNum = parseInt(input);
        if (reportTypeNum >= 1 && reportTypeNum <= 4) {
          setReportData({ ...reportData, type: reportTypes[reportTypeNum - 1].label });
          setTimeout(() => {
            addBotMessage('📍 ¿Dónde está el problema?\n\nEscribe la dirección o colonia.');
            setChatState('report_location');
          }, 500);
        }
        break;

      case 'report_location':
        setTimeout(() => {
          addBotMessage('¿Desde cuándo tienen este problema?', durationOptions);
          setChatState('report_duration');
        }, 500);
        break;

      case 'report_duration':
        const durationNum = parseInt(input);
        if (durationNum >= 1 && durationNum <= 3) {
          setReportData({ ...reportData, duration: durationOptions[durationNum - 1].label });
          setTimeout(() => {
            addBotMessage('¿Cuántas viviendas están afectadas aproximadamente?');
            setChatState('report_affected');
          }, 500);
        }
        break;

      case 'report_affected':
        const affected = parseInt(input) || 1;
        setReportData({ ...reportData, affected });
        setTimeout(() => {
          const reportId = `AH-2026-${Date.now().toString().slice(-4)}`;
          addBotMessage(
            `✅ Reporte registrado (#${reportId})\n\n📋 ${reportData.type}\n📍 Ubicación registrada\n⏱️ Duración: ${reportData.duration}\n🏠 ~${affected} viviendas afectadas\n\nTu reporte fue enviado a SACMEX. Te notificaremos cuando haya una actualización.`
          );
          setChatState('report_confirmed');
          setTimeout(() => {
            addBotMessage('💧 Mientras tanto, ¿necesitas pedir agua?', [
              { id: '1', label: 'Sí, ver pipas disponibles' },
              { id: 'menu', label: 'Volver al menú' },
            ]);
            setChatState('main_menu');
          }, 1500);
        }, 500);
        break;

      default:
        setTimeout(() => {
          addBotMessage('¿En qué te puedo ayudar?', mainMenuOptions);
          setChatState('main_menu');
        }, 500);
    }
  };

  const showProviders = () => {
    const availableProviders = mockProviders.filter(p => p.available);
    let message = `Encontré ${availableProviders.length} pipas disponibles en tu zona:\n\n`;
    
    availableProviders.forEach((provider, idx) => {
      message += `${idx + 1}️⃣ ${provider.name}\n`;
      message += `   💰 $${provider.pricePerLiter}/10,000L ⭐${provider.rating}\n`;
      message += `   ⏱️ Llega en ~${provider.estimatedArrival} min\n\n`;
    });

    message += '💳 Tienes un subsidio disponible de $200\n\n¿Cuál prefieres? Responde con el número.';
    
    addBotMessage(message);
    setChatState('show_providers');
  };

  return (
    <div className="min-h-screen bg-[#0b141a] flex flex-col">
      {/* Header */}
      <header className="bg-[#1f2c34] border-b border-[#2a373f] px-4 py-3 flex items-center gap-3">
        <Link to="/" className="text-[#00a884] hover:text-[#00c896]">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="w-10 h-10 bg-[#00a884] rounded-full flex items-center justify-center">
          <Droplets className="h-5 w-5 text-white" />
        </div>
        <div className="flex-1">
          <h1 className="text-white font-medium">AquaHub</h1>
          <p className="text-xs text-[#8696a0]">Bot de Servicios de Agua</p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/government" className="text-xs text-[#8696a0] hover:text-white transition-colors">
            Dashboard Gobierno
          </Link>
          <Link to="/company" className="text-xs text-[#8696a0] hover:text-white transition-colors">
            Dashboard Empresa
          </Link>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.02"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }}>
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex",
                message.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div className={cn(
                "max-w-[85%] rounded-lg px-3 py-2 shadow-sm",
                message.role === 'user' 
                  ? "bg-[#005c4b] text-white rounded-br-sm" 
                  : "bg-[#1f2c34] text-[#e9edef] rounded-bl-sm"
              )}>
                <p className="text-sm whitespace-pre-line">{message.content}</p>
                
                {/* Options */}
                {message.options && message.options.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.options.map((option) => (
                      <button
                        key={option.id}
                        onClick={() => handleOptionClick(option.id, option.label)}
                        className="w-full text-left px-3 py-2 bg-[#2a373f] hover:bg-[#3b4a54] rounded-lg text-sm text-[#00a884] transition-colors"
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                )}
                
                <div className="flex items-center justify-end gap-1 mt-1">
                  <span className="text-[10px] text-[#8696a0]">
                    {message.timestamp.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  {message.role === 'user' && (
                    <CheckCheck className="h-3.5 w-3.5 text-[#53bdeb]" />
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 bg-[#1f2c34] border-t border-[#2a373f]">
        <div className="flex items-center gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Escribe un mensaje..."
            className="flex-1 bg-[#2a373f] border-0 text-white placeholder:text-[#8696a0] focus-visible:ring-0 focus-visible:ring-offset-0"
          />
          <Button 
            type="submit" 
            size="icon" 
            className="bg-[#00a884] hover:bg-[#00c896] rounded-full"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}
