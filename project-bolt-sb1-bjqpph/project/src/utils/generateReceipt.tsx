import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import { Order } from '../types';

const styles = StyleSheet.create({
  page: {
    padding: 30,
  },
  header: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
  },
  orderInfo: {
    marginBottom: 20,
  },
  table: {
    display: 'table',
    width: '100%',
    borderStyle: 'solid',
    borderWidth: 1,
    borderColor: '#000',
  },
  tableRow: {
    flexDirection: 'row',
  },
  tableCell: {
    padding: 5,
    borderWidth: 1,
    borderColor: '#000',
  },
  total: {
    marginTop: 20,
    fontSize: 18,
    textAlign: 'right',
  },
});

interface ReceiptProps {
  order: Order;
}

export const Receipt: React.FC<ReceiptProps> = ({ order }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <Text style={styles.header}>Roriri Soft Canteen</Text>
      <View style={styles.orderInfo}>
        <Text>Order ID: {order.id}</Text>
        <Text>Date: {order.orderedAt.toLocaleDateString()}</Text>
      </View>
      <View style={styles.table}>
        {order.items.map((item) => (
          <View style={styles.tableRow} key={item.id}>
            <Text style={styles.tableCell}>{item.name}</Text>
            <Text style={styles.tableCell}>{item.quantity}</Text>
            <Text style={styles.tableCell}>₹{item.price}</Text>
            <Text style={styles.tableCell}>₹{item.price * item.quantity}</Text>
          </View>
        ))}
      </View>
      <Text style={styles.total}>Total: ₹{order.total}</Text>
    </Page>
  </Document>
);